import json
from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.messages import get_messages
from app.gamification.models import Course, CustomUser, SurveySection, ArtifactReview
from app.gamification.models.option_choice import OptionChoice
from app.gamification.models.question import Question
from app.gamification.models.question_option import QuestionOption
from app.gamification.models.registration import Registration
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.serializers import CourseSerializer
from app.gamification.views.api.course import CourseList, CourseDetail
from app.gamification.views.api.survey import SectionDetail
from app.gamification.views.api.answer import CreateArtifactAnswer



class CreateArtifactAnswerTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json', 'assignments.json', 'entities.json', 'membership.json', 'artifact.json', 'survey.json']
    @classmethod
    def setUpTestData(self):
        self.student_andrew_id = 'user1'
        self.student_password = 'user1-password'
        self.ta_andrew_id = 'user4'
        self.ta_password = 'user4-password'
        self.instructor_andrew_id = 'admin1'
        self.instructor_password = 'admin1-password'
        self.admin_andrew_id = 'admin2'
        self.admin_password = 'admin2-password'

        self.student = CustomUser.objects.get(
            andrew_id=self.student_andrew_id)  # pk = 3
        self.ta = CustomUser.objects.get(andrew_id=self.ta_andrew_id)
        self.instructor = CustomUser.objects.get(
            andrew_id=self.instructor_andrew_id)
        self.admin = CustomUser.objects.get(andrew_id=self.admin_andrew_id)

        self.slide_question = Question.objects.get(pk = 30)
        self.artifact_review = ArtifactReview.objects.get(id = 1)
        option_choice = OptionChoice(text = "")
        option_choice.save()

    def test_post_a_slide_review(self):
        self.client.login(
            andrew_id=self.student_andrew_id,
            password=self.student_password,
        )
        data = {
            'page':1,
            'answer_text': json.dumps(['test slide answer text'])
        }
        url = reverse(
            'create-artifact-answer', kwargs={'artifact_review_pk': self.artifact_review.id, 'question_pk': self.slide_question.id})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['page'], '1')
        self.assertEqual(response.json()['answer_text'], 'test slide answer text')

    def test_put_a_slide_review(self):
        self.client.login(
            andrew_id=self.student_andrew_id,
            password=self.student_password,
        )
        data = {
            'page':1,
            'answer_text': json.dumps(['test slide answer text'])
        }
        url = reverse(
            'create-artifact-answer', kwargs={'artifact_review_pk': self.artifact_review.id, 'question_pk': self.slide_question.id})
        response = self.client.put(url, data, content_type='application/json')
        data = {
            'page':1,
            'answer_text': json.dumps(['new text'])
        }
        url = reverse(
            'create-artifact-answer', kwargs={'artifact_review_pk': self.artifact_review.id, 'question_pk': self.slide_question.id})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['page'], '1')
        self.assertEqual(response.json()['answer_text'], 'new text')
    
    def test_get_a_slide_review(self):
        self.client.login(
            andrew_id=self.student_andrew_id,
            password=self.student_password,
        )
        data = {
            'page':1,
            'answer_text': json.dumps(['test slide answer text'])
        }
        url = reverse(
            'create-artifact-answer', kwargs={'artifact_review_pk': self.artifact_review.id, 'question_pk': self.slide_question.id})
        self.client.put(url, data, content_type='application/json')
        data = {
            'page':1,
            'answer_text': json.dumps(['new text'])
        }
        url = reverse(
            'create-artifact-answer', kwargs={'artifact_review_pk': self.artifact_review.id, 'question_pk': self.slide_question.id})
        self.client.put(url, data, content_type='application/json')
        data = {
            'page':2,
            'answer_text': json.dumps(['page 2 text'])
        }
        self.client.put(url, data, content_type='application/json')
        response = self.client.get(url, dict(), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['page'], '1')
        self.assertEqual(response.json()[0]['answer_text'], 'new text')
        self.assertEqual(response.json()[1]['page'], '2')
        self.assertEqual(response.json()[1]['answer_text'], 'page 2 text')

        