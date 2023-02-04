import pytz
from pytz import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from app.gamification.decorators import user_role_check
from app.gamification.forms import AssignmentForm
from app.gamification.models import Assignment, Course, Registration, Team, Membership, Artifact, Individual, FeedbackSurvey


LA = timezone('America/Los_Angeles')


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def assignment(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    userRole = Registration.objects.get(
        users=request.user, courses=course).userRole
    if request.method == 'GET':
        if userRole == Registration.UserRole.Student:
            infos = Assignment.objects.filter(course=course)
            user_is_individual = True
            try:
                registration = get_object_or_404(
                    Registration, users=request.user, courses=course_id)
                entity = Team.objects.get(
                    registration=registration, course=course)
                user_is_individual = False
            except Team.DoesNotExist:
                user_is_individual = True
            assignments = []
            for assignment in infos:
                assignment_type = assignment.assignment_type
                if assignment_type == 'Team' and user_is_individual:
                    print('individual user can not see this assignment')
                else:
                    if assignment.date_released != None and assignment.date_released.astimezone(pytz.timezone('America/Los_Angeles')) <= datetime.now().astimezone(
                            pytz.timezone('America/Los_Angeles')):
                        assignments.append(assignment)
                    elif assignment.date_released == None:
                        assignments.append(assignment)
        else:
            assignments = Assignment.objects.filter(course=course)
        info = []
        for a in assignments:
            feedback_survey = FeedbackSurvey.objects.filter(assignment=a)
            assign = dict()
            assign['assignment'] = a
            assign['feedback_survey'] = feedback_survey.count()
            if feedback_survey.count() == 1:
                feedback_survey_release_date = feedback_survey[0].date_released.astimezone(
                    pytz.timezone('America/Los_Angeles'))
                if feedback_survey_release_date <= datetime.now().astimezone(
                        pytz.timezone('America/Los_Angeles')):
                    assign['feedback_survey'] = 1
                else:
                    assign['feedback_survey'] = 0
            info.append(assign)
        context = {'infos': info,
                   "course_id": course_id,
                   "course": course,
                   "userRole": userRole}
        return render(request, 'assignment.html', context)

    else:
        form = AssignmentForm(request.POST, label_suffix='')
        if form.is_valid():
            assignment = form.save()
        assignments = Assignment.objects.filter(course=course)
        return redirect('edit_assignment', course_id, assignment.id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def delete_assignment(request, course_id, assignment_id):
    if request.method == 'GET':
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        assignment.delete()
        return redirect('assignment', course_id)
    else:
        return redirect('assignment', course_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA])
def edit_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    userRole = Registration.objects.get(
        users=request.user, courses=course_id).userRole
    if request.method == 'POST':
        form = AssignmentForm(
            request.POST, instance=assignment, label_suffix='')

        if form.is_valid():
            # TO-DO: update upload_time
            assignment = form.save()
        return redirect('assignment', course_id)

    if request.method == 'GET':
        form = AssignmentForm(instance=assignment)
        return render(request, 'edit_assignment.html', {'course_id': course_id, 'form': form, 'userRole': userRole})

    else:
        return redirect('assignment', course_id)


@login_required
@user_role_check(user_roles=[Registration.UserRole.Instructor, Registration.UserRole.TA, Registration.UserRole.Student])
def view_assignment(request, course_id, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    userRole = Registration.objects.get(
        users=request.user, courses=course_id).userRole
    registration = get_object_or_404(
        Registration, users=request.user, courses=course_id)
    course = get_object_or_404(Course, pk=course_id)
    andrew_id = request.user.andrew_id
    assignment_type = assignment.assignment_type
    feedback_survey = FeedbackSurvey.objects.filter(assignment=assignment)
    print('feedback_survey.count()', feedback_survey.count())
    if userRole == Registration.UserRole.Instructor or userRole == Registration.UserRole.TA:
        assignment_id = assignment.id
        context = {'course_id': course_id,
                   'userRole': userRole,
                   'assignment': assignment,
                   'assignment_id': assignment_id,
                   'andrew_id': andrew_id,
                   }
        return render(request, 'view_assignment_admin.html', context)
    if assignment_type == "Individual":
        try:
            entity = Individual.objects.get(
                registration=registration, course=course)
        except Individual.DoesNotExist:
            # Create an Individual entity for the user
            individual = Individual(course=course)
            individual.save()
            membership = Membership(student=registration, entity=individual)
            membership.save()
            entity = Individual.objects.get(
                registration=registration, course=course)
    elif assignment_type == "Team":
        try:
            entity = Team.objects.get(registration=registration, course=course)
        except Team.DoesNotExist:
            # TODO: Alert: you need to be a member of the team to upload the artifact
            print("you need to be a member of the team to upload the artifact")
            return redirect('assignment', course_id)
    else:
        return redirect('assignment', course_id)

    try:
        artifacts = Artifact.objects.filter(
            assignment=assignment, entity=entity)
        latest_artifact = artifacts.latest('upload_time')
        artifact_id = latest_artifact.id
    except Artifact.DoesNotExist:
        latest_artifact = "None"
        artifact_id = None

    # if artifact exist
    if artifact_id != None:
        latest_artifact_filename = latest_artifact.file.name.split('/')[-1]
    else:
        latest_artifact_filename = ""
    assignment_id = assignment.id
    context = {'course_id': course_id,
               'userRole': userRole,
               'assignment': assignment,
               'latest_artifact': latest_artifact,
               'assignment_id': assignment_id,
               'artifact_id': artifact_id,
               'andrew_id': andrew_id,
               'latest_artifact_filename': latest_artifact_filename}
    return render(request, 'view_assignment.html', context)



