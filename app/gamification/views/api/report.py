from django.http import HttpResponse
from app.gamification import serializers
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.contrib import messages
from app.gamification.serializers import EntitySerializer, UserSerializer, CourseSerializer
from django.shortcuts import get_object_or_404
from app.gamification.models import Assignment, Course, CustomUser, Registration, Team, Membership, Artifact, ArtifactReview, Entity, Team, Individual, Answer
from app.gamification.models.question_option import QuestionOption
from app.gamification.models.question import Question
from app.gamification.models.answer import Answer, ArtifactFeedback

import pytz
import json
from pytz import timezone
from datetime import datetime
from app.gamification.utils import get_user_pk
from collections import defaultdict

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class IsAdminOrReadOnly(permissions.BasePermission):
    '''
    Custom permission to only allow users to view read-only information.
    Admin users are allowed to view and edit information.
    '''

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class ViewReport(generics.ListCreateAPIView):
    # queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get report information",
        tags=['reports'],
    )
    def get(self, request, course_id, assignment_id, *args, **kwargs):
        if 'andrew_id' in request.query_params:
            def artifact_result(artifact_pk):
                artifact = get_object_or_404(Artifact, pk=artifact_pk)
                assignment = artifact.assignment
                survey_template = assignment.survey_template
                sections = survey_template.sections

                confidence = dict()
                confidence['sum'] = 0
                artifact_reviews = ArtifactReview.objects.filter(
                    artifact=artifact)
                for artifact_review in artifact_reviews:
                    answers = Answer.objects.filter(
                        artifact_review=artifact_review)
                    for answer in answers:
                        if answer.question_option.question.text == 'Your confidence' and answer.question_option.question.question_type == Question.QuestionType.NUMBER:
                            confidence[artifact_review.pk] = answer.answer_text
                            confidence['sum'] += int(answer.answer_text)
                answers = {}
                for section in sections:
                    answers[section.title] = dict()
                    for question in section.questions:
                        if question.question_type == Question.QuestionType.NUMBER and question.text == 'Your confidence':
                            continue
                        answers[section.title][question.text] = dict()
                        answers[section.title][question.text]['question_type'] = question.question_type
                        answers[section.title][question.text]['answers'] = []
                        artifact_reviews = ArtifactReview.objects.filter(
                            artifact=artifact)

                        if question.question_type == Question.QuestionType.MULTIPLECHOICE or question.question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                            question_options = question.options
                            for question_option in question_options:
                                answer_text = question_option.option_choice.text
                                count = Answer.objects.filter(
                                    artifact_review__in=artifact_reviews, question_option=question_option).count()
                                if count > 0:
                                    answers[section.title][question.text]['answers'].append(
                                        {answer_text: count}
                                    )
                        elif question.question_type == Question.QuestionType.NUMBER and question.text != 'Your confidence':
                            question_option = get_object_or_404(
                                QuestionOption, question=question)

                            count = 0
                            res = 0
                            for artifact_review in artifact_reviews:
                                text_answers = Answer.objects.filter(
                                    artifact_review=artifact_review, question_option=question_option)
                                if text_answers.count() > 0:
                                    count += 1
                                    res += int(text_answers[0].answer_text) * \
                                        int(confidence[artifact_review.pk])
                            if confidence['sum'] != 0:
                                answers[section.title][question.text]['answers'].append(
                                    str(round(res/(confidence['sum']), 1)))

                        elif question.question_type == Question.QuestionType.SLIDEREVIEW:
                            answers[section.title][question.text]['answers'] = defaultdict(
                                list)
                            question_option = get_object_or_404(
                                QuestionOption, question=question)
                            for artifact_review in artifact_reviews:
                                text_answers = ArtifactFeedback.objects.filter(
                                    artifact_review=artifact_review, question_option=question_option)
                                for answer in text_answers:
                                    answers[section.title][question.text]['answers'][answer.page].append(
                                        answer.answer_text)

                        else:
                            question_option = get_object_or_404(
                                QuestionOption, question=question)
                            for artifact_review in artifact_reviews:
                                text_answers = Answer.objects.filter(
                                    artifact_review=artifact_review, question_option=question_option)
                                for answer in text_answers:
                                    answers[section.title][question.text]['answers'].append(
                                        answer.answer_text)
                return answers

            def artifact_answer_multiple_choice_list(artifact_pk):
                # data = {"label":["a", "b", "c", "d"], "sections":{"section_name": {"question_name": [2,3,1,4]}}}
                answers = []
                artifacts_reviews = ArtifactReview.objects.filter(
                    artifact_id=artifact_pk)
                for artifact_review in artifacts_reviews:
                    answer = Answer.objects.filter(
                        artifact_review_id=artifact_review.pk).order_by('pk')
                    answers.extend(answer)

                choice_labels = set()
                scale_list_7 = ['strongly disagree', 'disagree', 'weakly disagree',
                                'neutral', 'weakly agree', 'agree', 'strongly agree']
                scale_list_5 = ['strongly disagree', 'disagree',
                                'neutral', 'agree', 'strongly agree']
                scale_list_3 = ['disagree', 'neutral', 'agree']

                choice_labels_scale = set()
                number_of_scale = 0
                for answer in answers:
                    if answer.question_option.question.question_type == 'SCALEMULTIPLECHOICE':
                        number_of_scale = answer.question_option.question.number_of_scale
                    elif answer.question_option.question.question_type == 'MULTIPLECHOICE':
                        choice_labels.add(
                            answer.question_option.option_choice.text)
                scale_list_input = []
                if number_of_scale == 7:
                    scale_list_input = scale_list_7
                elif number_of_scale == 5:
                    scale_list_input = scale_list_5
                elif number_of_scale == 3:
                    scale_list_input = scale_list_3
                else:
                    pass
                for scale_answer in scale_list_input:
                    choice_labels_scale.add(scale_answer)

                result = {"label": list(choice_labels), "label_scale": scale_list_input, "sections": defaultdict(
                    dict), "sections_scale": defaultdict(dict), "number_of_scale": number_of_scale}
                for answer in answers:
                    if answer.question_option.question.question_type == 'MULTIPLECHOICE':
                        if answer.question_option.question.text not in result["sections"][answer.question_option.question.section.title].keys():
                            result["sections"][answer.question_option.question.section.title][answer.question_option.question.text] = [
                                0 for i in range(len(choice_labels))]
                        option_index = list(choice_labels).index(
                            answer.question_option.option_choice.text)
                        result["sections"][answer.question_option.question.section.title][answer.question_option.question.text][option_index] += 1
                    elif answer.question_option.question.question_type == 'SCALEMULTIPLECHOICE':
                        if answer.question_option.question.text not in result["sections_scale"][answer.question_option.question.section.title].keys():
                            result["sections_scale"][answer.question_option.question.section.title][answer.question_option.question.text] = [
                                0 for i in range(len(choice_labels_scale))]
                        option_index = list(choice_labels_scale).index(
                            answer.question_option.option_choice.text)
                        result["sections_scale"][answer.question_option.question.section.title][
                            answer.question_option.question.text][option_index] += 1
                return result

            def retrive_grade(artifact_pk):
                dummy_data = {
                    'user_index': 0,
                    'data': [[95.0, 80.0, 88.0, 90, 0], [90.0, 85.0, 90.0, 95.0], [85.0, 90.0, 95.0, 100.0], [85.0, 90.0, 95.0, 100.0]]
                }

                return dummy_data  # TODO: implement this function

            # individual report
            andrew_id = request.query_params['andrew_id']
            user = get_object_or_404(CustomUser, andrew_id=andrew_id)
            course = get_object_or_404(Course, pk=course_id)
            registration = get_object_or_404(
                Registration, users=user, courses=course)
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment_type = assignment.assignment_type

            if assignment_type == "Individual":
                entity = Individual.objects.get(
                    registration=registration, course=course)
                team_name = str(andrew_id)
            elif assignment_type == "Team":
                entity = Team.objects.get(
                    registration=registration, course=course)
                team_name = entity.name

            artifact_id = None
            try:
                artifact = Artifact.objects.get(
                    assignment=assignment, entity=entity)
                artifact_id = artifact.pk
            except Artifact.DoesNotExist:
                return Response("Artifact does not exist", status=status.HTTP_404_NOT_FOUND)

            context = {'andrew_id': user.andrew_id,
                       'course_name': course.course_name,
                       'team_name': team_name,
                       'artifact_result_ret': artifact_result(artifact_id),
                       'artifact_answer_multiple_choice_list_ret': artifact_answer_multiple_choice_list(artifact_id),
                       # dummy data preserved for pointing system
                       'point': retrive_grade(artifact_id),
                       }
            return Response(context, status=status.HTTP_200_OK)
        else:
            # assignment report
            course = get_object_or_404(Course, pk=course_id)
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            assignment_type = assignment.assignment_type
            user_id = get_user_pk(request)
            user = get_object_or_404(CustomUser, id=user_id)
            userRole = Registration.objects.get(
                users=user, courses=course).userRole
            students = []
            teams = []
            if assignment_type == "Individual":
                registrations = Registration.objects.filter(
                    courses=course_id, userRole=Registration.UserRole.Student)
                counter = 0
                student_row = []
                for registration in registrations:
                    student_row.append(registration.users.andrew_id)
                    counter += 1
                    if counter == 4:
                        students.append(student_row)
                        counter = 0
                        student_row = []
                students.append(student_row)

            elif assignment_type == "Team":
                all_teams = Team.objects.filter(course=course)
                team_row = []
                counter = 0
                for team in all_teams:
                    team_row.append(team.name)
                    counter += 1
                    if counter == 4:
                        teams.append(team_row)
                        counter = 0
                        team_row = []
                teams.append(team_row)

            # students or teams is an empty list
            context = {
                'userRole': userRole,
                'students': students,
                'teams': teams
            }
            return Response(context, status=status.HTTP_200_OK)
