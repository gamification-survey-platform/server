import datetime
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
import pytz

from app.gamification.models import CustomUser, Course, Registration, Assignment, QuestionOption
from app.gamification.models.entity import Team
from app.gamification.models.feedback_survey import FeedbackSurvey
from app.gamification.models.membership import Membership
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.survey_section import SurveySection
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.tests.views.pages.utils import LogInUser


class SurveyTemplateTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json',
                'membership.json', 'entities.json', 'assignments.json']

    def test_get_survey_template(self):
        survey_template = SurveyTemplate(
            name='Test Survey',
        )
        survey_template.save()
        self.assertEqual(survey_template.name, 'Test Survey')

    def test_get_sections_property(self):
        survey_template = SurveyTemplate(
            name='Test Survey',
        )
        survey_template.save()
        survey_section = SurveySection(
            template=survey_template,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        survey_section.save()
        self.assertEqual(survey_template.sections.count(), 1)
        self.assertEqual(
            survey_template.sections.first().title, 'Test Section')
        self.assertEqual(
            survey_template.sections.first().description, 'Test Description')
        self.assertEqual(survey_template.sections.first().is_required, True)


class FeedbackSurveyTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json',
                'membership.json', 'entities.json', 'assignments.json']

    def setUp(self):
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021')
        self.assignment = Assignment.objects.get(
            assignment_name='Chat Room Iteration 1')
        self.survey_template = SurveyTemplate(
            name='Test Survey',
        )
        self.survey_template.save()

    def test_get_feedback_survey(self):
        feedback_survey = FeedbackSurvey(
            template=self.survey_template,
            assignment=self.assignment,
        )
        feedback_survey.save()
        self.assertEqual(feedback_survey.template.name,
                         self.survey_template.name)
        self.assertEqual(feedback_survey.assignment.assignment_name,
                         self.assignment.assignment_name)


class SurveySectionTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json',
                'membership.json', 'entities.json', 'assignments.json']

    def setUp(self):
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021')
        self.assignment = Assignment.objects.get(
            assignment_name='Chat Room Iteration 1')
        self.survey_template = SurveyTemplate(
            name='Test Survey',
        )
        self.survey_template.save()

    def test_get_survey_section(self):
        survey_section = SurveySection(
            template=self.survey_template,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        survey_section.save()
        self.assertEqual(survey_section.title, 'Test Section')
        self.assertEqual(survey_section.description, 'Test Description')
        self.assertEqual(survey_section.is_required, True)

    def test_get_questions_property(self):
        survey_section = SurveySection(
            template=self.survey_template,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        survey_section.save()
        survey_question = Question(
            section=survey_section,
            text='Test Question',
            question_type=Question.QuestionType.MULTIPLECHOICE,
            is_required=True,
            is_multiple=True,
        )
        survey_question.save()
        self.assertEqual(
            survey_section.questions.count(), 1)
        self.assertEqual(
            survey_section.questions.first().text, 'Test Question')
        self.assertEqual(
            survey_section.questions.first().question_type, 'MULTIPLECHOICE')
        self.assertEqual(survey_section.questions.first().is_required, True)


class SurveyQuestionTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json',
                'membership.json', 'entities.json', 'assignments.json']

    def setUp(self):
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021')
        self.assignment = Assignment.objects.get(
            assignment_name='Chat Room Iteration 1')
        self.survey_template = SurveyTemplate(
            name='Test Survey',
        )
        self.survey_template.save()
        self.survey_section = SurveySection(
            template=self.survey_template,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        self.survey_section.save()

    def test_get_survey_question(self):
        survey_question = Question(
            section=self.survey_section,
            text='Test Question',
            question_type=Question.QuestionType.MULTIPLECHOICE,
            is_required=True,
            is_multiple=True,
        )
        survey_question.save()
        self.assertEqual(survey_question.text, 'Test Question')
        self.assertEqual(survey_question.question_type, 'MULTIPLECHOICE')
        self.assertEqual(survey_question.is_required, True)
        self.assertEqual(survey_question.is_multiple, True)

    def test_get_option_choice_property(self):
        survey_question = Question(
            section=self.survey_section,
            text='Test Question',
            question_type=Question.QuestionType.MULTIPLECHOICE,
            is_required=True,
            is_multiple=True,
        )
        survey_question.save()
        survey_option = OptionChoice(
            text='Test Option',
        )
        survey_option.save()

        question_option = QuestionOption(
            question=survey_question,
            option_choice=survey_option,
        )
        question_option.save()

        self.assertEqual(survey_question.options.count(), 1)
        self.assertEqual(
            survey_question.options.first().option_choice.text, 'Test Option')


class QuestionOptionTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json',
                'membership.json', 'entities.json', 'assignments.json']

    def setUp(self):
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021')
        self.assignment = Assignment.objects.get(
            assignment_name='Chat Room Iteration 1')
        self.survey_template = SurveyTemplate(
            name='Test Survey',
        )
        self.survey_template.save()
        self.survey_section = SurveySection(
            template=self.survey_template,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        self.survey_section.save()
        self.survey_question = Question(
            section=self.survey_section,
            text='Test Question',
            question_type=Question.QuestionType.MULTIPLECHOICE,
            is_required=True,
            is_multiple=True,
        )
        self.survey_question.save()

        self.survey_option = OptionChoice(
            text='Test Option',
        )
        self.survey_option.save()

    def test_get_question_option(self):
        question_option = QuestionOption(
            question=self.survey_question,
            option_choice=self.survey_option,
        )
        question_option.save()
        self.assertEqual(question_option.question.text, 'Test Question')
        self.assertEqual(question_option.option_choice.text, 'Test Option')


class OptionChoiceTest(TestCase):

    def test_get_option_choice(self):
        option_choice = OptionChoice(
            text='Test Option',
        )
        option_choice.save()
        self.assertEqual(option_choice.text, 'Test Option')
