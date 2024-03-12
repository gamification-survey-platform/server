import re

import spacy
import yake
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.models.answer import Answer, ArtifactFeedback
from app.gamification.models.artifact import Artifact
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.models.assignment import Assignment
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.serializers.answer import AnswerSerializer
from app.gamification.utils.s3 import generate_presigned_url


class ArtifactAnswerKeywordList(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all answers keywords for a specific artifact",
        tags=["reports"],
    )
    def get(self, request, artifact_pk, *args, **kwargs):
        nlp = spacy.load("en_core_web_sm")
        answers = []
        artifacts_reviews = ArtifactReview.objects.filter(artifact_id=artifact_pk)
        for artifact_review in artifacts_reviews:
            answer = Answer.objects.filter(artifact_review_id=artifact_review.pk).order_by("pk")
            answers.extend(answer)
        text = ""
        for answer in answers:
            number_answers = ["MULTIPLECHOICE", "NUMBER"]
            if answer.option_choice.question.question_type not in number_answers:
                answer_content = " " + answer.answer_text + ". "
                text += answer_content
        doc = nlp(text)
        nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

        language = "en"
        max_ngram_size = 3
        deduplication_threshold = 0.9
        numOfKeywords = 50
        custom_kw_extractor = yake.KeywordExtractor()
        custom_kw_extractor = yake.KeywordExtractor(
            lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None
        )
        keywords = custom_kw_extractor.extract_keywords(text)
        result = {}
        for word in keywords:
            if (
                bool(re.search(r"\s", word[0])) is False
                and word[0] not in nouns
                and word[0] not in verbs
                or bool(re.search(r"\s", word[0])) is True
            ):
                result[word[0]] = int((1 - word[1]) * 10)
        return Response(result)


class ArtifactAnswerMultipleChoiceList(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all multiple choice data for a given artifact",
        tags=["reports"],
        responses={
            200: openapi.Response(
                description="Multiple choice data for a given artifact",
                examples={
                    "application/json": {
                        "label": ["a", "b", "c", "d"],
                        "sections": {"section_name": {"question_name": [2, 3, 1, 4]}},
                    }
                },
            )
        },
    )
    def get(self, request, artifact_pk, *args, **kwargs):
        answers = []
        artifacts_reviews = ArtifactReview.objects.filter(artifact_id=artifact_pk)
        for artifact_review in artifacts_reviews:
            answer = Answer.objects.filter(artifact_review_id=artifact_review.pk).order_by("pk")
            answers.extend(answer)

        choice_labels = set()
        scale_list_7 = [
            "strongly disagree",
            "disagree",
            "weakly disagree",
            "neutral",
            "weakly agree",
            "agree",
            "strongly agree",
        ]
        scale_list_5 = ["strongly disagree", "disagree", "neutral", "agree", "strongly agree"]
        scale_list_3 = ["disagree", "neutral", "agree"]
        number_of_scale_dict = {3: scale_list_3, 5: scale_list_5, 7: scale_list_7}
        result = {
            "sections": {},
        }
        for answer in answers:
            question_text = answer.option_choice.question.text
            section_title = answer.option_choice.question.section.title
            question_type = answer.option_choice.question.question_type
            if (
                question_type == Question.QuestionType.MULTIPLECHOICE
                or question_type == Question.QuestionType.SCALEMULTIPLECHOICE
                or question_type == Question.QuestionType.MULTIPLESELECT
            ):
                if (
                    question_type == Question.QuestionType.MULTIPLECHOICE
                    or question_type == Question.QuestionType.MULTIPLESELECT
                ):
                    option_choices = OptionChoice.objects.filter(question=answer.option_choice.question)
                    choice_labels = [option_choice.text for option_choice in option_choices]
                elif question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                    number_of_scale = answer.option_choice.question.number_of_scale
                    choice_labels = number_of_scale_dict[number_of_scale]
                # Check if section_title in sections
                if section_title not in result["sections"]:
                    result["sections"][section_title] = {}
                # Check if question_text in sections
                if question_text not in result["sections"][section_title].keys():
                    result["sections"][section_title][question_text] = {}
                    result["sections"][section_title][question_text]["counts"] = [0 for i in range(len(choice_labels))]
                    result["sections"][section_title][question_text]["labels"] = choice_labels
                if (
                    question_type == Question.QuestionType.MULTIPLECHOICE
                    or question_type == Question.QuestionType.MULTIPLESELECT
                ):
                    option_index = list(choice_labels).index(answer.option_choice.text)
                elif question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                    option_index = list(choice_labels).index(answer.answer_text)
                result["sections"][section_title][question_text]["counts"][option_index] += 1
        return Response(result)


class ArtifactAnswerDetail(generics.GenericAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get all data for a given artifact",
        tags=["reports"],
        responses={
            200: openapi.Response(
                description="Multiple choice data for a given artifact",
                examples={},
            )
        },
    )
    def get(self, request, course_id, assignment_id, artifact_pk, *args, **kwargs):
        artifacts_reviews = ArtifactReview.objects.filter(
            artifact_id=artifact_pk, status=ArtifactReview.ArtifactReviewType.COMPLETED
        )
        assignment = get_object_or_404(Assignment, id=assignment_id)
        survey_template = assignment.survey
        data = dict()
        data["pk"] = survey_template.pk
        data["name"] = survey_template.name
        data["artifact_pk"] = artifact_pk
        artifact = Artifact.objects.get(id=artifact_pk)
        data["instructions"] = survey_template.instructions
        data["sections"] = []
        for section in survey_template.sections:
            curr_section = dict()
            curr_section["pk"] = section.pk
            curr_section["title"] = section.title
            curr_section["is_required"] = section.is_required
            curr_section["questions"] = []
            for question in section.questions:
                curr_question = dict()
                curr_question["pk"] = question.pk
                curr_question["text"] = question.text
                curr_question["is_required"] = question.is_required
                curr_question["question_type"] = question.question_type
                curr_question["phrased_positively"] = question.phrased_positively
                curr_question["gamified"] = False
                curr_question["artifact_reviews"] = []
                for completed_artifact_review in artifacts_reviews:
                    answer_filter = {
                        "artifact_review_id": completed_artifact_review.pk,
                        "option_choice__question": question,
                    }
                    answers = (
                        Answer.objects.filter(**answer_filter)
                        if question.question_type != Question.QuestionType.SLIDEREVIEW
                        else ArtifactFeedback.objects.filter(**answer_filter)
                    )
                    curr_question["artifact_reviews"].append([])
                    for answer in answers:
                        answer_data = {}
                        answer_data["page"] = (
                            answer.page if question.question_type == Question.QuestionType.SLIDEREVIEW else None
                        )
                        answer_data["text"] = answer.answer_text
                        answer_data["artifact_review_id"] = completed_artifact_review.pk
                        reviewer_registration = completed_artifact_review.user
                        answer_data["artifact_reviewer_id"] = reviewer_registration.user.pk
                        curr_question["artifact_reviews"][-1].append(answer_data)
                if question.question_type == Question.QuestionType.SLIDEREVIEW:
                    key = artifact.file.name
                    path = f"http://{settings.ALLOWED_HOSTS[2]}:8000{artifact.file.url}"

                    if settings.USE_S3:
                        path = generate_presigned_url(key, http_method="GET")
                    curr_question["file_path"] = path
                if (
                    question.question_type == Question.QuestionType.MULTIPLECHOICE
                    or question.question_type == Question.QuestionType.MULTIPLESELECT
                ):
                    curr_question["option_choices"] = []
                    for option_choice in question.options:
                        curr_option_choice = dict()
                        curr_option_choice["pk"] = option_choice.pk
                        curr_option_choice["text"] = option_choice.text
                        curr_question["option_choices"].append(curr_option_choice)

                elif question.question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
                    curr_question["number_of_scale"] = question.number_of_scale
                elif question.question_type == Question.QuestionType.MULTIPLETEXT:
                    curr_question["number_of_text"] = question.number_of_text
                curr_section["questions"].append(curr_question)
            data["sections"].append(curr_section)
        return Response(data)
