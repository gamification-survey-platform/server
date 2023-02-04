import collections
import json
import yake
import spacy
import re
from django.utils import timezone
from rest_framework import generics, mixins, permissions
from rest_framework.response import Response
from django.contrib import messages
from django.shortcuts import get_object_or_404
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


class AnswerList(generics.ListAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    # permission_classes = [IsAdminOrReadOnly]


class AnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, answer_pk, *args, **kwargs):
        answer = get_object_or_404(Answer, id=answer_pk)
        serializer = self.get_serializer(answer)
        return Response(serializer.data)

    def put(self, request, answer_pk, *args, **kwargs):
        answer = get_object_or_404(Answer, id=answer_pk)
        answer_text = request.data.get('answer_text')
        answer.answer_text = answer_text
        answer.save()
        serializer = self.get_serializer(answer)
        return Response(serializer.errors, status=400)

    def delete(self, request, answer_pk, *args, **kwargs):
        answer = get_object_or_404(Answer, id=answer_pk)
        answer.delete()
        return Response(status=204)


class FeedbackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArtifactFeedback.objects.all()
    serializer_class = ArtifactFeedbackSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, feedback_pk, *args, **kwargs):
        feedback = get_object_or_404(ArtifactFeedback, id=feedback_pk)
        serializer = self.get_serializer(feedback)
        return Response(serializer.data)

    def put(self, request, feedback_pk, *args, **kwargs):
        feedback = get_object_or_404(ArtifactFeedback, id=feedback_pk)
        answer_text = request.data.get('answer_text')
        feedback.answer_text = answer_text
        feedback.save()
        serializer = self.get_serializer(feedback)
        return Response(serializer.errors, status=400)

    def delete(self, request, feedback_pk, *args, **kwargs):
        feedback = get_object_or_404(ArtifactFeedback, id=feedback_pk)
        feedback.delete()
        return Response(status=204)


class ArtifactAnswerList(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, artifact_review_pk, *args, **kwargs):
        answer = Answer.objects.filter(
            artifact_review_id=artifact_review_pk).order_by('pk')
        serializer = self.get_serializer(answer)
        return Response(serializer.data)


class CreateArtifactAnswer(generics.RetrieveUpdateAPIView):
    queryset = Answer.objects.all()
    serializer_class = CreateAnswerSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, artifact_review_pk, question_pk, * args, **kwargs):
        question = get_object_or_404(Question, id=question_pk)
        if question.question_type == Question.QuestionType.SLIDEREVIEW:
            self.serializer_class = ArtifactFeedbackSerializer
            artifact_review = get_object_or_404(
                ArtifactReview, id=artifact_review_pk)
            question_options = question.options
            answers = []
            for question_option in question_options:
                if ArtifactFeedback.objects.filter(question_option=question_option, artifact_review=artifact_review).count() > 0:
                    answer = ArtifactFeedback.objects.filter(
                        question_option=question_option, artifact_review=artifact_review)
                    answers.extend(answer)
            serializer = self.get_serializer(answers, many=True)
            return Response(serializer.data)
        else:
            artifact_review = get_object_or_404(
                ArtifactReview, id=artifact_review_pk)
            question_options = question.options
            answers = []
            for question_option in question_options:
                if Answer.objects.filter(question_option=question_option, artifact_review=artifact_review).count() > 0:
                    answer = Answer.objects.filter(
                        question_option=question_option, artifact_review=artifact_review)
                    answers.extend(answer)
            serializer = self.get_serializer(answers, many=True)
            return Response(serializer.data)

    def put(self, request, artifact_review_pk, question_pk, *args, **kwargs):
        # Multiple Choice text -> option_text
        artifact_review = get_object_or_404(
            ArtifactReview, id=artifact_review_pk)
        # Text input -> answer_text []
        answer_texts = json.loads(request.data.get('answer_text'))
        if '' in answer_texts:
            answer_texts = [i for i in answer_texts if i != '']
        # get_object_or_404
        question = Question.objects.get(id=question_pk)
        question_type = question.question_type
        if question_type == Question.QuestionType.MULTIPLECHOICE or question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
            # delete original answer
            if len(answer_texts) == 0:
                return Response()
            question_options = question.options.all()
            
            # question_options = ['a', 'b', 'c', 'd']
            for question_option in question_options:
                if len(answer_texts) == 0:
                    break
                if Answer.objects.filter(question_option=question_option, artifact_review=artifact_review).count() > 0:
                    answer = Answer.objects.get(
                        question_option=question_option, artifact_review=artifact_review)
                    # answer {answer_text= 'b', question_option= question_option(optionChoice=b, question=question), artifact_review= aritfact_review}
                    # check answer_texts whether empty
                    # answer_text = ['a']
                    if len(answer_texts) > 0:
                        current_answer = answer_texts.pop(0)
                        answer.answer_text = current_answer
                        question_option = QuestionOption.objects.get(
                            option_choice=OptionChoice.objects.get(text=current_answer), question=question)
                        answer.question_option = question_option
                        answer.save()
                    else:
                        # original answers more than new answers
                        answer.delete()
            # new answers more than original answers
            while len(answer_texts) != 0:
                current_answer = answer_texts.pop(0)
                question_option = QuestionOption.objects.get(
                    option_choice=OptionChoice.objects.get(text=current_answer), question=question)
                answer = Answer(answer_text=current_answer,
                                question_option=question_option, artifact_review=artifact_review)
                answer.save()
            serializer = self.get_serializer(answer)
            return Response(serializer.data)

        elif question_type == Question.QuestionType.FIXEDTEXT or question_type == Question.QuestionType.MULTIPLETEXT or question_type == Question.QuestionType.TEXTAREA or question_type == Question.QuestionType.NUMBER:
            answer = None
            question_option = question.options[0]
            answers = Answer.objects.filter(
                question_option=question_option, artifact_review=artifact_review)
            for answer in answers:
                if len(answer_texts) > 0:
                    current_answer = answer_texts.pop(0)
                    answer.answer_text = current_answer
                    answer.save()
                else:
                    # original answers more than new answers
                    answer.delete()

            while len(answer_texts) != 0:
                current_answer = answer_texts.pop(0)
                answer = Answer(answer_text=current_answer,
                                question_option=question_option, artifact_review=artifact_review)
                answer.save()
            serializer = self.get_serializer(answer)
            return Response(serializer.data)
        else:
            page = request.data.get('page')
            if len(answer_texts) == 0:
                return Response()
            answer_text = answer_texts[0]
            self.serializer_class = ArtifactFeedbackSerializer
            question_option = get_object_or_404(
                QuestionOption, question=question)
            # all answers of the slide question
            answer, _ = ArtifactFeedback.objects.get_or_create(
                question_option=question_option,
                artifact_review=artifact_review,
                page=page,
            )
            answer.answer_text = answer_text
            answer.save()
            serializer = self.get_serializer(answer)
            return Response(serializer.data)


class ArtifactReviewList(generics.ListCreateAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    # permission_classes = [IsAdminOrReadOnly]


class ArtifactReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, artifact_review_id, *args, **kwargs):
        artifact_review = get_object_or_404(
            ArtifactReview, artifact_review_pk=artifact_review_id)
        serializer = self.get_serializer(artifact_review)
        return Response(serializer.data)

    def delete(self, request, artifact_review_id, *args, **kwargs):
        artifact_review = get_object_or_404(
            ArtifactReview, id=artifact_review_id)
        artifact_review.delete()
        return Response(status=204)


class CreateArtifactReview(generics.ListCreateAPIView):
    queryset = ArtifactReview.objects.all()
    serializer_class = ArtifactReviewSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, artifact_pk, registration_pk, *args, **kwargs):
        artifact_review = get_object_or_404(
            ArtifactReview, artifact_id=artifact_pk, user_id=registration_pk)
        serializer = self.get_serializer(artifact_review)
        return Response(serializer.data)

    def post(self, request, artifact_pk, registration_pk, *args, **kwargs):
        artifact = get_object_or_404(Artifact, id=artifact_pk)
        registration = get_object_or_404(Registration, id=registration_pk)
        artifact_review = Answer.objects.get_or_create(
            artifact=artifact,
            user=registration,
        )
        serializer = self.get_serializer(artifact_review)
        return Response(serializer.data)


class ArtifactResult(generics.ListAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get(self, request, artifact_pk, *args, **kwargs):
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
                # dict{option_choice.text: number}
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
        data = json.dumps(answers)
        return Response(data)


class SurveyComplete(generics.CreateAPIView):
    def post(self, request, artifact_review_pk, *args, **kwargs):
        artifact_review = get_object_or_404(
            ArtifactReview, id=artifact_review_pk)
        now = datetime.now().astimezone(pytz.timezone('America/Los_Angeles'))
        artifact = artifact_review.artifact
        assignment = artifact.assignment
        feedback_survey = FeedbackSurvey.objects.get(assignment=assignment)
        due_date = feedback_survey.date_due.astimezone(
            pytz.timezone('America/Los_Angeles'))
        if now > due_date:
            artifact_review.status = ArtifactReview.ArtifactReviewType.LATE
        else:
            artifact_review.status = ArtifactReview.ArtifactReviewType.COMPLETED
        artifact_review.save()
        return Response(status=204)


class CheckAllDone(generics.GenericAPIView):

    def post(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(Question, pk=question_pk)
        is_required = question.is_required
        answer_texts = json.loads(request.data.get('answer_text'))
        answer_texts = [text for text in answer_texts if text != '']
        if is_required and not answer_texts:
            return Response(status=400)

        return Response(status=200)

class ArtifactAnswerKeywordList(generics.ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, artifact_pk, *args, **kwargs):
        nlp = spacy.load("en_core_web_sm")
        answers = []
        artifacts_reviews = ArtifactReview.objects.filter(artifact_id = artifact_pk)
        for artifact_review in artifacts_reviews:
            answer = Answer.objects.filter(
                artifact_review_id=artifact_review.pk).order_by('pk')
            answers.extend(answer)
        text = ""
        for answer in answers:
            number_answers = ['MULTIPLECHOICE', 'NUMBER']
            if answer.question_option.question.question_type not in number_answers:
                answer_content = " "+ answer.answer_text + ". "
                text += answer_content
        doc = nlp(text)
        nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

        kw_extractor = yake.KeywordExtractor()
        language = "en"
        max_ngram_size = 3
        deduplication_threshold = 0.9
        numOfKeywords = 10
        custom_kw_extractor = yake.KeywordExtractor()
        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
        keywords = custom_kw_extractor.extract_keywords(text)
        result = {}
        for word in keywords:
            if bool(re.search(r"\s", word[0]))==False and word[0] not in nouns and word[0] not in verbs or bool(re.search(r"\s", word[0]))==True:
                result[word[0]] = int((1 - word[1]) * 10)
        return Response(result)

class ArtifactAnswerMultipleChoiceList(generics.ListCreateAPIView):
    # data = {"label":["a", "b", "c", "d"], "sections":{"section_name": {"question_name": [2,3,1,4]}}}
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    def get(self, request, artifact_pk, *args, **kwargs):
        answers = []
        artifacts_reviews = ArtifactReview.objects.filter(artifact_id = artifact_pk)
        for artifact_review in artifacts_reviews:
            answer = Answer.objects.filter(
                artifact_review_id=artifact_review.pk).order_by('pk')
            answers.extend(answer)
        # choice_labels = set()
        #[section_title][MULTIPLECHOICE/SCALEMULTIPLECHOICE][label/answer_text]
        # for answer in answers:
        #     section_name = answer.question_option.question.section
        #     if answer.question_option.question.question_type == 'SCALEMULTIPLECHOICE':
        #         print("test")
        #     elif answer.question_option.question.question_type == 'MULTIPLECHOICE':
        #         choice_labels.add((section_name, answer.question_option.option_choice.text))
        # choice_labels_list = list(choice_labels)
        # result = collections.defaultdict(list)
        # for section_name, choice in choice_labels_list:
        #     result[section_name].append(choice)
        # return Response(result)
        
        choice_labels = set()
        scale_list_7 = ['strongly disagree', 'disagree', 'weakly disagree', 'neutral', 'weakly agree', 'agree', 'strongly agree']
        scale_list_5 = ['strongly disagree', 'disagree', 'neutral', 'agree', 'strongly agree']
        scale_list_3 = ['disagree', 'neutral', 'agree']

        
        # choice_labels_scale = set('agree', 'weakly agree', 'disagree', 'neutral', 'strongly disagree', 'strongly agree', 'weakly disagree')
        choice_labels_scale = set()
        number_of_scale = 0
        for answer in answers:
            # print(answer.question_option.question.section)
            # print(answer.question_option.question.question_type)
            if answer.question_option.question.question_type == 'SCALEMULTIPLECHOICE':
                # choice_labels_scale.add(answer.question_option.option_choice.text)
                number_of_scale = answer.question_option.question.number_of_scale
            elif answer.question_option.question.question_type == 'MULTIPLECHOICE':
                choice_labels.add(answer.question_option.option_choice.text)
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
            
        result = {"label": list(choice_labels), "label_scale": scale_list_input, "sections": collections.defaultdict(dict), "sections_scale": collections.defaultdict(dict), "number_of_scale": number_of_scale}
        for answer in answers:
            if answer.question_option.question.question_type == 'MULTIPLECHOICE':
                if answer.question_option.question.text not in result["sections"][answer.question_option.question.section.title].keys():
                    result["sections"][answer.question_option.question.section.title][answer.question_option.question.text]= [0 for i in range(len(choice_labels))]
                option_index = list(choice_labels).index(answer.question_option.option_choice.text)
                result["sections"][answer.question_option.question.section.title][answer.question_option.question.text][option_index] += 1
            elif answer.question_option.question.question_type == 'SCALEMULTIPLECHOICE':
                if answer.question_option.question.text not in result["sections_scale"][answer.question_option.question.section.title].keys():
                    result["sections_scale"][answer.question_option.question.section.title][answer.question_option.question.text]= [0 for i in range(len(choice_labels_scale))]
                option_index = list(choice_labels_scale).index(answer.question_option.option_choice.text)
                result["sections_scale"][answer.question_option.question.section.title][answer.question_option.question.text][option_index] += 1
        return Response(result)
        

