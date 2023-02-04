import json
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.question_option import QuestionOption
from app.gamification.models.registration import Registration
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.serializers.survey import OptionChoiceSerializer, OptionChoiceWithoutNumberOfTextSerializer, QuestionSerializer, SectionSerializer, SurveySerializer, TemplateSectionSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        registrations = Registration.objects.filter(users=request.user)
        for registration in registrations:
            if registration.userRole == Registration.UserRole.Instructor:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        registrations = Registration.objects.filter(users=request.user)
        for registration in registrations:
            if registration.userRole == Registration.UserRole.Instructor:
                return True
        return False


class SurveyList(generics.ListCreateAPIView):
    queryset = SurveyTemplate.objects.all()
    serializer_class = SurveySerializer
    # permission_classes = [IsAdminOrReadOnly]


class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveyTemplate.objects.all()
    serializer_class = SurveySerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=survey_pk)
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

    def put(self, request, survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=survey_pk)
        name = request.data.get('name').strip()
        if name == '':
            content = {'message': 'Survey name cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        instructions = request.data.get('instructions')
        other_info = request.data.get('other_info')
        survey.name = name
        survey.instructions = instructions
        survey.other_info = other_info
        survey.save()
        serializer = self.get_serializer(survey)
        return Response(serializer.data)

    def delete(self, request, survey_pk, *args, **kwargs):
        survey = get_object_or_404(SurveyTemplate, id=survey_pk)
        survey.delete()
        return Response(status=204)


class SurveySectionList(generics.ListCreateAPIView):
    queryset = SurveyTemplate.objects.all()
    serializer_class = SectionSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, survey_pk, *args, **kwargs):
        sections = SurveySection.objects.filter(
            template=survey_pk).order_by('pk')
        serializer = self.get_serializer(sections, many=True)
        return Response(serializer.data)

    def post(self, request, survey_pk, *args, **kwargs):
        title = request.data.get('title').strip()
        if title == '':
            content = {'message': 'Section title cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if title == 'Artifact':
            content = {
                'message': 'Artifact is a reserved section title. Please choose another title.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        description = request.data.get('description')
        is_required = True if request.data.get(
            'is_required') == 'true' else False
        survey = get_object_or_404(SurveyTemplate, id=survey_pk)
        section = SurveySection(template=survey, title=title,
                                description=description, is_required=is_required)
        section.save()
        serializer = self.get_serializer(section)
        return Response(serializer.data)


class SectionList(generics.ListAPIView):
    queryset = SurveySection.objects.all()
    serializer_class = SectionSerializer
    # permission_classes = [IsAdminOrReadOnly]


class SectionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SurveySection.objects.all()
    serializer_class = SectionSerializer

    def get(self, request, section_pk, *args, **kwargs):
        section = get_object_or_404(
            SurveySection, id=section_pk)
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    def put(self, request, section_pk, *args, **kwargs):
        section = get_object_or_404(
            SurveySection, id=section_pk)
        title = request.data.get('title').strip()
        if title == '':
            content = {'message': 'Section title cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        description = request.data.get('description')
        is_required = True if request.data.get(
            'is_required') == 'true' else False
        section.title = title
        section.description = description
        section.is_required = is_required
        section.save()
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    def delete(self, request, section_pk, *args, **kwargs):
        section = get_object_or_404(
            SurveySection, id=section_pk)
        section.delete()
        return Response(status=204)


class SectionQuestionList(generics.ListCreateAPIView):
    queryset = SurveySection.objects.all()
    serializer_class = QuestionSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, section_pk, *args, **kwargs):
        questions = Question.objects.filter(section=section_pk).order_by('pk')
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request, section_pk, *args, **kwargs):
        text = request.data.get('text').strip()
        if text == '':
            content = {'message': 'Question text cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        is_required = True if request.data.get(
            'is_required') == 'true' else False
        is_multiple = True if request.data.get(
            'is_multiple') == 'true' else False
        dependent_question = request.data.get('dependent_question') if request.data.get(
            'dependent_question') != '' else None
        question_type = request.data.get('question_type')
        number_of_scale = request.data.get('number_of_scale', -1)
        section = SurveySection.objects.get(id=section_pk)
        question = Question(
            text=text, is_required=is_required, is_multiple=is_multiple, number_of_scale=number_of_scale, dependent_question=dependent_question, question_type=question_type, section=section)
        question.save()
        if question_type == Question.QuestionType.SCALEMULTIPLECHOICE:
            if question.number_of_scale == 3:
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="agree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="neutral")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="disagree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
            elif question.number_of_scale == 5:
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="strongly agree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="agree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="neutral")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="disagree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="strongly disagree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
            else:
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="strongly agree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="agree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="weakly agree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="neutral")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="weakly disagree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="disagree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text="strongly disagree")
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()
        serializer = self.get_serializer(question)
        return Response(serializer.data)


class QuestionList(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # permission_classes = [IsAdminOrReadOnly]


class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(
            Question, id=question_pk)
        serializer = self.get_serializer(question)
        return Response(serializer.data)

    def put(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(
            Question, id=question_pk)
        text = request.data.get('text').strip()
        if text == '':
            content = {'message': 'Question text cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        is_required = True if request.data.get(
            'is_required') == 'true' else False
        is_multiple = True if request.data.get(
            'is_multiple') == 'true' else False
        dependent_question = request.data.get('dependent_question') if request.data.get(
            'dependent_question') != '' else None
        question_type = request.data.get('question_type')
        question.text = text
        question.is_required = is_required
        question.is_multiple = is_multiple
        question.dependent_question = dependent_question
        question.question_type = question_type
        question.save()
        serializer = self.get_serializer(question)
        return Response(serializer.data)

    def delete(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(Question, id=question_pk)
        question.delete()
        return Response(status=204)


class QuestionOptionList(generics.ListCreateAPIView, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Question.objects.all()
    serializer_class = OptionChoiceSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(Question, id=question_pk)
        options = question.option_choices.all()
        for option in options:
            number_of_text = QuestionOption.objects.get(
                question=question, option_choice=option).number_of_text

            option.number_of_text = number_of_text
        serializer = self.get_serializer(options, many=True)
        return Response(serializer.data)

    def put(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(Question, id=question_pk)
        original_option_choices = question.option_choices.all()
        original_texts = [
            option_choice.text for option_choice in original_option_choices]
        texts = json.loads(request.body.decode())
        for text in texts:
            if text not in original_texts:
                option_choice, _ = OptionChoice.objects.get_or_create(
                    text=text)
                question_option = QuestionOption(
                    option_choice=option_choice, question=question)
                question_option.save()

        for original_option_choice in original_option_choices:
            if original_option_choice.text not in texts:
                question_option = QuestionOption.objects.get(
                    question=question, option_choice=original_option_choice)
                question_option.delete()

        option_choices = question.option_choices.all()
        for option_choice in option_choices:
            number_of_text = QuestionOption.objects.get(
                question=question, option_choice=option_choice).number_of_text
            option_choice.number_of_text = number_of_text
        serializer = self.get_serializer(option_choices, many=True)
        return Response(serializer.data)

    def post(self, request, question_pk, *args, **kwargs):
        question = get_object_or_404(Question, id=question_pk)
        text = request.data.get('text').strip()
        number_of_text = request.data.get('number_of_text', 1)
        number_of_scale = request.data.get('number_of_scale', -1)
        option_choice, _ = OptionChoice.objects.get_or_create(text=text)
        if number_of_scale != -1:
            question.number_of_scale = number_of_scale
            question.save()
        QuestionOption.objects.get_or_create(
            option_choice=option_choice,
            question=question,
            number_of_text=number_of_text
        )
        option_choice.number_of_text = number_of_text
        serializer = self.get_serializer(option_choice)
        return Response(serializer.data)


class QuestionOptionDetail(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Question.objects.all()
    serializer_class = OptionChoiceSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def put(self, request, question_pk, option_pk, *args, **kwargs):
        question_option = get_object_or_404(
            QuestionOption, option_choice_id=option_pk, question_id=question_pk)
        text = request.data.get('text').strip()
        option, _ = OptionChoice.objects.get_or_create(text=text)
        question_option.option_choice = option
        number_of_text = request.data.get('number_of_text', 1)
        question_option.number_of_text = number_of_text
        question_option.save()

        option.number_of_text = number_of_text
        serializer = self.get_serializer(option)
        return Response(serializer.data)

    def delete(self, request, question_pk, option_pk, *args, **kwargs):
        question_option = get_object_or_404(
            QuestionOption, option_choice_id=option_pk, question_id=question_pk)
        question_option.delete()
        return Response(status=204)


class OptionList(generics.ListCreateAPIView):
    queryset = OptionChoice.objects.all()
    serializer_class = OptionChoiceWithoutNumberOfTextSerializer
    # permission_classes = [IsAdminOrReadOnly]


class OptionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OptionChoice.objects.all()
    serializer_class = OptionChoiceSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get(self, request, option_pk, *args, **kwargs):
        option = get_object_or_404(OptionChoice, id=option_pk)
        serializer = self.get_serializer(option)
        return Response(serializer.data)

    def put(self, request, option_pk, *args, **kwargs):
        option = get_object_or_404(OptionChoice, id=option_pk)
        text = request.data.get('text').strip()
        if text == '':
            content = {'message': 'Question text cannot be empty'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        option.text = text
        option.save()
        serializer = self.get_serializer(option)
        return Response(serializer.data)

    def delete(self, request, option_pk, *args, **kwargs):
        option_choice = get_object_or_404(OptionChoice, id=option_pk)
        option_choice.delete()
        return Response(status=204)


class TemplateSectionList(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        survey_template = get_object_or_404(
            SurveyTemplate, is_template=True)
        data = dict()
        data['pk'] = survey_template.pk
        data['is_template'] = survey_template.is_template
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
        return Response(json.dumps(data))


class SurveyGetInfo(generics.ListAPIView):
    def get(self, request, survey_pk, *args, **kwargs):
        survey_template = get_object_or_404(
            SurveyTemplate, pk=survey_pk)
        data = dict()
        data['pk'] = survey_pk
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
        return Response(json.dumps(data))
