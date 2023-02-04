import pytz
from pytz import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.utils import parse_datetime
from app.gamification.decorators import user_role_check
from app.gamification.models import Assignment, Course, Registration, Membership, Artifact, FeedbackSurvey, Question, OptionChoice, QuestionOption
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.survey_template import SurveyTemplate

LA = timezone('America/Los_Angeles')


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def add_survey(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    if request.method == 'POST':
        survey_template_name = request.POST.get('template_name').strip()
        survey_template_instruction = request.POST.get('instructions')
        survey_template_other_info = request.POST.get('other_info')
        feedback_survey_date_released = parse_datetime(
            request.POST.get('date_released'))
        feedback_survey_date_due = parse_datetime(request.POST.get('date_due'))
        survey_template = SurveyTemplate(
            name=survey_template_name, instructions=survey_template_instruction, other_info=survey_template_other_info)
        survey_template.save()
        feedback_survey = FeedbackSurvey(
            assignment=assignment,
            template=survey_template,
            date_released=feedback_survey_date_released,
            date_due=feedback_survey_date_due
        )
        feedback_survey.save()

        if survey_template_name == "Default Template":

            default_survey_template = get_object_or_404(
                SurveyTemplate, is_template=True, name="Survey Template")
            for default_section in default_survey_template.sections:
                section = SurveySection(template=survey_template,
                                        title=default_section.title,
                                        description=default_section.description,
                                        is_required=default_section.is_required,
                                        )
                section.save()
                for default_question in default_section.questions:
                    question = Question(section=section,
                                        text=default_question.text,
                                        question_type=default_question.question_type,
                                        dependent_question=default_question.dependent_question,
                                        is_required=default_question.is_required,
                                        is_multiple=default_question.is_multiple,
                                        )
                    question.save()
                    for default_option in default_question.options:
                        question_option = QuestionOption(
                            question=question,
                            option_choice=default_option.option_choice,
                            number_of_text=default_option.number_of_text,
                        )
                        question_option.save()

        else:

            # Automatically create a section and question for artifact
            artifact_section = SurveySection.objects.create(
                template=survey_template,
                title='Artifact',
                description='Please review the artifact.',
                is_required=False,
            )
            artifact_question = Question.objects.create(
                section=artifact_section,
                text='',
                question_type=Question.QuestionType.SLIDEREVIEW,
            )
            empty_option, _ = OptionChoice.objects.get_or_create(text='')
            QuestionOption.objects.create(
                question=artifact_question, option_choice=empty_option)

        return redirect('edit_survey', course_id, assignment_id)
    else:
        feedback_survey = FeedbackSurvey.objects.filter(assignment=assignment)
        if feedback_survey.count() > 0:
            return redirect('edit_survey', course_id, assignment_id)
        return render(request, 'add_survey.html', {'course_id': course_id, 'assignment_id': assignment_id})


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def edit_survey_template(request, course_id, assignment_id):
    if request.method == 'POST':

        survey_template_name = request.POST.get('template_name')
        survey_template_instruction = request.POST.get('instructions')
        survey_template_other_info = request.POST.get('other_info')
        feedback_survey_date_released = parse_datetime(
            request.POST.get('date_released'))
        feedback_survey_date_due = parse_datetime(request.POST.get('date_due'))
        feedback_survey = FeedbackSurvey.objects.get(
            assignment_id=assignment_id
        )
        survey_template = feedback_survey.template

        survey_template.name = survey_template_name
        survey_template.instructions = survey_template_instruction
        survey_template.other_info = survey_template_other_info
        survey_template.save()

        feedback_survey.template = survey_template
        feedback_survey.date_released = feedback_survey_date_released
        feedback_survey.date_due = feedback_survey_date_due
        feedback_survey.save()
        return redirect('edit_survey', course_id, assignment_id)
    else:
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        feedback_survey = FeedbackSurvey.objects.get(assignment=assignment)
        survey_template = feedback_survey.template
        context = {
            'course_id': course_id,
            'assignment_id': assignment_id,
            'survey_template_name': survey_template.name,
            'survey_template_instruction': survey_template.instructions,
            'survey_template_other_info': survey_template.other_info,
            'feedback_survey_date_released': feedback_survey.date_released,
            'feedback_survey_date_due': feedback_survey.date_due
        }
        return render(request, 'edit_survey_template.html', context)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def edit_survey(request, course_id, assignment_id):
    if request.method == 'GET':
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        feedback_survey = get_object_or_404(
            FeedbackSurvey, assignment=assignment)
        survey_template = feedback_survey.template.pk
        return render(request, 'edit_survey.html', {'survey_pk': survey_template, 'course_id': course_id, 'assignment_id': assignment_id})
    else:
        return render(request, 'edit_survey.html')


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def edit_preview_survey(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    feedback_survey = get_object_or_404(
        FeedbackSurvey, assignment=assignment)
    survey_template = feedback_survey.template.pk
    return render(request, 'edit_preview_survey.html', {'survey_pk': survey_template})


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def fill_survey(request, course_id, assignment_id, artifact_review_id):
    user = request.user
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    artifact = ArtifactReview.objects.get(
        pk=artifact_review_id).artifact.file
    feedback_survey = get_object_or_404(
        FeedbackSurvey, assignment=assignment)
    survey_template = feedback_survey.template.pk
    return render(request, 'fill_survey.html', {'survey_pk': survey_template, 'artifact_review_pk': artifact_review_id, 'course_id': course_id, 'assignment_id': assignment_id, 'picture': artifact})


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def review_survey(request, course_id, assignment_id):
    #team, button_survey
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    feedback_survey = get_object_or_404(FeedbackSurvey, assignment=assignment)
    assignment_type = assignment.assignment_type
    artifacts = Artifact.objects.filter(assignment=assignment)
    # find artifact_review(registration, )
    registration = get_object_or_404(Registration, users=user, courses=course)
    artifact_reviews = []
    for artifact in artifacts:
        artifact_reviews.extend(ArtifactReview.objects.filter(
            artifact=artifact, user=registration))
    infos = []
    for artifact_review in artifact_reviews:
        artifact_review_with_name = dict()
        artifact = artifact_review.artifact
        feedback_survey_released_date = feedback_survey.date_released.astimezone(
            pytz.timezone('America/Los_Angeles'))
        if feedback_survey_released_date <= datetime.now().astimezone(
                pytz.timezone('America/Los_Angeles')):
            artifact_review_with_name["artifact_review_pk"] = artifact_review.pk
            artifact_review_with_name["status"] = artifact_review.status
            if assignment_type == "Team":
                entity = artifact.entity
                team = entity.team
                artifact_review_with_name["name"] = team.name

            else:
                entity = artifact.entity
                name = Membership.objects.get(
                    entity=entity).student.users.name_or_andrew_id()
                artifact_review_with_name["name"] = name
            infos.append(artifact_review_with_name)

    return render(request, 'survey_list.html', {'course_id': course_id, 'assignment_id': assignment_id, 'infos': infos, 'assignment_type': assignment_type})
