import collections
import json
from django.forms import model_to_dict
import yake
import spacy
import re
from django.utils import timezone
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from django.contrib import messages
from django.shortcuts import get_object_or_404
from app.gamification.models.assignment import Assignment
from app.gamification.models.course import Course
from app.gamification.models.entity import Team
from app.gamification.models.membership import Membership
from app.gamification.models.user import CustomUser
from app.gamification.utils import get_user_pk, check_survey_status
from ...models.feedback_survey import FeedbackSurvey
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.artifact import Artifact
from app.gamification.models.answer import Answer, ArtifactFeedback
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.question import Question
from app.gamification.models.question_option import QuestionOption
from app.gamification.models.registration import Registration
from app.gamification.serializers.answer import AnswerSerializer, ArtifactReviewSerializer, ArtifactFeedbackSerializer, CreateAnswerSerializer
from collections import defaultdict
import pytz
from datetime import datetime


class ArtifactReviewList(generics.RetrieveAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, course_id, assignment_id, *args, **kwargs):
        user_id = get_user_pk(request)
        user = get_object_or_404(CustomUser, id=user_id)
        course = get_object_or_404(Course, id=course_id)
        assignment = get_object_or_404(Assignment, id=assignment_id)
        registration = get_object_or_404(
            Registration, users=user, courses=course)
        artifacts = Artifact.objects.filter(
            assignment_id=assignment_id)
        artifact_reviews = []
        for artifact in artifacts:
            try:
                artifact_review = ArtifactReview.objects.get(
                    artifact=artifact, user=registration)
            except ArtifactReview.DoesNotExist:
                artifact_review = ArtifactReview(
                    artifact=artifact, user=registration)
                artifact_review.save()
            artifact_review_dict = model_to_dict(artifact_review)
            if assignment.assignment_type == 'Individual':
                artifact_review_dict['reviewing'] = Membership.objects.get(
                    entity=artifact.entity).student.users.name_or_andrew_id()
            else:
                artifact_review_dict['reviewing'] = artifact.entity.team.name
            artifact_reviews.append(artifact_review_dict)
        return Response(artifact_reviews, status=status.HTTP_200_OK)


class ArtifactReviewDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, course_id, assignment_id,  artifact_review_pk, *args, **kwargs):
        artifact_review = get_object_or_404(
            ArtifactReview, id=artifact_review_pk)
        assignment = get_object_or_404(Assignment, id=assignment_id)
        survey_template = assignment.survey_template
        if not survey_template:
            return Response({"error": "No survey template, instructor should create survey first"}, status=status.HTTP_400_BAD_REQUEST)
        data = dict()
        data['pk'] = survey_template.pk
        data['name'] = survey_template.name
        data['instructions'] = survey_template.instructions
        data['other_info'] = survey_template.other_info
        data['sections'] = []
        for section in survey_template.sections:
            curr_section = dict()
            curr_section['pk'] = section.pk
            curr_section['title'] = section.title
            curr_section['is_required'] = section.is_required
            curr_section['questions'] = []
            for question in section.questions:
                curr_question = dict()
                curr_question['pk'] = question.pk
                curr_question['text'] = question.text
                curr_question['is_required'] = question.is_required
                curr_question['question_type'] = question.question_type
                curr_question['answer'] = []
                answers = Answer.objects.filter(
                    artifact_review_id=artifact_review_pk, question_option__question=question)
                for answer in answers:
                    curr_question['answer'].append(
                        answer.answer_text)
                if question.question_type == Question.QuestionType.MULTIPLECHOICE:
                    curr_question['option_choices'] = []
                    for option_choice in question.options:
                        curr_option_choice = dict()
                        curr_option_choice['pk'] = option_choice.option_choice.pk
                        curr_option_choice['text'] = option_choice.option_choice.text
                        curr_question['option_choices'].append(
                            curr_option_choice)

                elif question.question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                    curr_question['number_of_scale'] = question.number_of_scale
                else:
                    question_option = get_object_or_404(
                        QuestionOption, question=question)
                    curr_question['number_of_text'] = question_option.number_of_text
                curr_section['questions'].append(curr_question)
            data['sections'].append(curr_section)
        return Response(data)

    def patch(self, request, course_id, assignment_id, artifact_review_pk, *args, **kwargs):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        artifact_status = check_survey_status(assignment)
        artifact_review_detail = request.data.get('artifact_review_detail')
        artifact_review = get_object_or_404(
            ArtifactReview, id=artifact_review_pk)
        # delete old answers
        Answer.objects.filter(artifact_review_id=artifact_review_pk).delete()
        artifact_review.status = artifact_status
        artifact_review.save()
        for answer in artifact_review_detail:
            question_pk = answer["question_pk"]
            answer_text = answer["answer_text"]
            question = Question.objects.get(id=question_pk)
            question_type = question.question_type
            is_required = question.is_required
            if is_required and answer_text == "":
                return Response({"error": "Please answer all required questions."}, status=status.HTTP_400_BAD_REQUEST)
            if answer_text == "":
                continue
            if question_type == Question.QuestionType.MULTIPLECHOICE or question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                question_options = question.options.all()
                for question_option in question_options:
                    if question_option.option_choice.text == answer_text:
                        answer = Answer()
                        answer.question_option = question_option
                        answer.artifact_review = artifact_review
                        answer.answer_text = answer_text
                        answer.save()
                        break

            elif question_type == Question.QuestionType.FIXEDTEXT or question_type == Question.QuestionType.MULTIPLETEXT or question_type == Question.QuestionType.TEXTAREA or question_type == Question.QuestionType.NUMBER:
                question_option = question.options[0]
                answer = Answer()
                answer.question_option = question_option
                answer.artifact_review = artifact_review
                answer.answer_text = answer_text
                answer.save()
            else:
                # question type: slide review
                pass
        return Response(status=status.HTTP_200_OK)
