import collections
import re

import spacy
import yake
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from app.gamification.models.answer import Answer
from app.gamification.models.artifact_review import ArtifactReview
from app.gamification.serializers.answer import AnswerSerializer


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
    # data = {"label":["a", "b", "c", "d"], "sections":{"section_name": {"question_name": [2,3,1,4]}}}
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

        # choice_labels_scale = set('agree', 'weakly agree', 'disagree', 'neutral',
        # 'strongly disagree', 'strongly agree', 'weakly disagree')
        choice_labels_scale = set()
        number_of_scale = 0
        for answer in answers:
            if answer.option_choice.question.question_type == "SCALEMULTIPLECHOICE":
                number_of_scale = answer.option_choice.question.number_of_scale
            elif answer.option_choice.question.question_type == "MULTIPLECHOICE":
                choice_labels.add(answer.option_choice.option_choice.text)
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

        result = {
            "label": list(choice_labels),
            "label_scale": scale_list_input,
            "sections": collections.defaultdict(dict),
            "sections_scale": collections.defaultdict(dict),
            "number_of_scale": number_of_scale,
        }
        for answer in answers:
            if answer.option_choice.question.question_type == "MULTIPLECHOICE":
                if (
                    answer.option_choice.question.text
                    not in result["sections"][answer.option_choice.question.section.title].keys()
                ):
                    result["sections"][answer.option_choice.question.section.title][
                        answer.option_choice.question.text
                    ] = [0 for i in range(len(choice_labels))]
                option_index = list(choice_labels).index(answer.option_choice.option_choice.text)
                result["sections"][answer.option_choice.question.section.title][answer.option_choice.question.text][
                    option_index
                ] += 1
            elif answer.option_choice.question.question_type == "SCALEMULTIPLECHOICE":
                if (
                    answer.option_choice.question.text
                    not in result["sections_scale"][answer.option_choice.question.section.title].keys()
                ):
                    result["sections_scale"][answer.option_choice.question.section.title][
                        answer.option_choice.question.text
                    ] = [0 for i in range(len(choice_labels_scale))]
                option_index = list(choice_labels_scale).index(answer.option_choice.option_choice.text)
                result["sections_scale"][answer.option_choice.question.section.title][
                    answer.option_choice.question.text
                ][option_index] += 1
        return Response(result)
