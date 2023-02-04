from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.messages import get_messages
from app.gamification.models import Course, CustomUser, SurveySection
from app.gamification.models.question import Question
from app.gamification.models.registration import Registration
from app.gamification.models.survey_template import SurveyTemplate
from app.gamification.serializers import CourseSerializer
from app.gamification.views.api.course import CourseList, CourseDetail
from app.gamification.views.api.survey import SectionDetail


class RetrieveSurveyListTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

    def test_student_can_get_all_surveys(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()

        self.url = reverse('survey-list')
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), list)
        self.assertEqual(len(self.response.json()), 1)
        self.assertEqual(self.response.json()[0]['name'], 'Test Survey')
        self.assertEqual(self.response.json()[
                         0]['instructions'], 'Test Instructions')
        self.assertEqual(self.response.json()[
                         0]['other_info'], 'Test Other Info')


class UpdateSurveyListTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.url = reverse('survey-list')

    def test_instructor_can_post_survey(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        data = {
            'name': 'Test Survey',
            'instructions': 'Test Instructions',
            'other_info': 'Test Other Info',
        }
        self.client.post(self.url, data)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), list)
        self.assertEqual(len(self.response.json()), 1)
        self.assertEqual(self.response.json()[0]['name'], 'Test Survey')
        self.assertEqual(self.response.json()[
                         0]['instructions'], 'Test Instructions')
        self.assertEqual(self.response.json()[
                         0]['other_info'], 'Test Other Info')

    def test_ta_cannot_post_survey(self):
        ta = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.TA,
        )
        ta.save()
        data = {
            'name': 'Test Survey',
            'instructions': 'Test Instructions',
            'other_info': 'Test Other Info',
        }
        self.client.post(self.url, data)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), list)
        self.assertEqual(len(self.response.json()), 0)

    def test_instructor_post_a_survey_without_a_name(self):
        ta = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.TA,
        )
        ta.save()
        data = {
            'name': '',
            'instructions': 'Test Instructions',
            'other_info': 'Test Other Info',
        }
        self.client.post(self.url, data)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), list)
        self.assertEqual(len(self.response.json()), 0)

    def test_instructor_can_post_survey_without_instructions_and_other_info(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        data = {
            'name': 'Test Survey',
            'instructions': '',
            'other_info': '',
        }
        self.client.post(self.url, data)
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), list)
        self.assertEqual(len(self.response.json()), 1)
        self.assertEqual(self.response.json()[0]['name'], 'Test Survey')
        self.assertEqual(self.response.json()[
                         0]['instructions'], '')
        self.assertEqual(self.response.json()[
                         0]['other_info'], '')


class RetrieveSurveyDetailTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

    def test_student_can_get_survey_detail(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()

        self.url = reverse(
            'survey-detail', kwargs={'survey_pk': self.survey.id})
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), dict)
        self.assertEqual(self.response.json()['name'], 'Test Survey')
        self.assertEqual(self.response.json()['instructions'],
                         'Test Instructions')
        self.assertEqual(self.response.json()['other_info'], 'Test Other Info')

    def test_instructor_can_get_survey_detail(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        self.url = reverse(
            'survey-detail', kwargs={'survey_pk': self.survey.id})
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(self.response.json(), dict)
        self.assertEqual(self.response.json()['name'], 'Test Survey')
        self.assertEqual(self.response.json()['instructions'],
                         'Test Instructions')
        self.assertEqual(self.response.json()['other_info'], 'Test Other Info')

    def test_instructor_cannot_get_survey_with_an_invalid_pk(self):
        INVALID_PK = 2
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        self.url = reverse(
            'survey-detail', kwargs={'survey_pk': INVALID_PK})
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 404)


class UpdateSurveyDetailTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

    def test_instructor_can_update_survey_detail(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        url = reverse(
            'survey-detail', kwargs={'survey_pk': self.survey.id})
        data = {
            'name': 'Test Survey 1 ',
            'instructions': 'Test Instructions 1 ',
            'other_info': 'Test Other Info 1',
        }
        self.client.put(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['name'], 'Test Survey 1 ')
        self.assertEqual(response.json()['instructions'],
                         'Test Instructions 1 ')
        self.assertEqual(response.json()[
                         'other_info'], 'Test Other Info 1')

    def test_student_cannot_update_survey_detail(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()

        url = reverse(
            'survey-detail', kwargs={'survey_pk': self.survey.id})
        data = {
            'name': 'Test Survey 1 ',
            'instructions': 'Test Instructions 1 ',
            'other_info': 'Test Other Info 1',
        }
        self.client.put(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['name'], 'Test Survey')
        self.assertEqual(response.json()['instructions'],
                         'Test Instructions')
        self.assertEqual(response.json()[
                         'other_info'], 'Test Other Info')

    def test_instructor_can_delete_survey_detail(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        url = reverse(
            'survey-detail', kwargs={'survey_pk': self.survey.id})
        data = {
            'name': 'Test Survey 1 ',
            'instructions': 'Test Instructions 1 ',
            'other_info': 'Test Other Info 1',
        }
        self.client.delete(url, data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_student_cannot_delete_survey_detail(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()

        url = reverse(
            'survey-detail', kwargs={'survey_pk': self.survey.id})
        data = {
            'name': 'Test Survey 1 ',
            'instructions': 'Test Instructions 1 ',
            'other_info': 'Test Other Info 1',
        }
        self.client.delete(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['name'], 'Test Survey')
        self.assertEqual(response.json()['instructions'],
                         'Test Instructions')
        self.assertEqual(response.json()[
                         'other_info'], 'Test Other Info')


class RetrieveSectionListTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

        self.section = SurveySection(
            template=self.survey,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        self.section.save()

    def test_student_can_get_section_list(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()
        response = self.client.get(reverse(
            'survey-section-list', kwargs={'survey_pk': self.survey.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['title'], 'Test Section')
        self.assertEqual(response.json()[0]['description'], 'Test Description')
        self.assertEqual(response.json()[0]['is_required'], True)


class UpdateSectionListTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

    def test_instructor_can_add_a_section(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        url = reverse(
            'survey-section-list', kwargs={'survey_pk': self.survey.id})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        self.client.post(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['title'], 'Test Section 1 ')
        self.assertEqual(response.json()[0]['description'],
                         'Test Description 1 ')
        self.assertEqual(response.json()[0]['is_required'], True)

    def test_student_cannot_add_a_section(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()

        url = reverse(
            'survey-section-list', kwargs={'survey_pk': self.survey.id})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': True,
        }
        self.client.post(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)

    def test_instructor_cannot_add_a_section_with_an_invalid_survey_pk(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        url = reverse(
            'survey-section-list', kwargs={'survey_pk': 100})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_instructor_cannot_add_a_section_without_a_title(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()

        url = reverse(
            'survey-section-list', kwargs={'survey_pk': self.survey.id})
        data = {
            'title': '',
            'description': 'Test Description 1 ',
            'is_required': True,
        }
        self.client.post(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)
        self.assertEqual(list(get_messages(response.wsgi_request))[
                         0].message, 'Title cannot be empty')


class RetrieveSurveySectionDetailTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

        self.section = SurveySection(
            template=self.survey,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        self.section.save()

    def test_student_can_get_section_detail(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()
        response = self.client.get(reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': self.section.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['title'], 'Test Section')
        self.assertEqual(response.json()['description'], 'Test Description')
        self.assertEqual(response.json()['is_required'], True)


class UpdateSurveySectionDetailTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

        self.section = SurveySection(
            template=self.survey,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        self.section.save()

    def test_instructor_can_update_a_section(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': self.section.id})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        self.client.put(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['title'], 'Test Section 1 ')
        self.assertEqual(response.json()['description'],
                         'Test Description 1 ')
        self.assertEqual(response.json()['is_required'], True)

    def test_student_cannot_update_a_section(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': self.section.id})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        self.client.put(url, data, content_type='application/json')
        response = self.client.get(url)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json()['title'], 'Test Section')
        self.assertEqual(response.json()['description'],
                         'Test Description')
        self.assertEqual(response.json()['is_required'], True)

    def test_instructor_cannot_update_a_section_with_an_invalid_survey_pk(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': 100, 'section_pk': self.section.id})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_instructor_cannot_update_a_section_without_section_title(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': self.section.id})
        data = {
            'title': '',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(list(get_messages(response.wsgi_request))[
                         0].message, 'Title cannot be empty')

    def test_instructor_cannot_update_a_section_with_an_invalid_section_pk(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': 100})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_instructor_can_delete_a_section(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': self.section.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_student_cannot_delete_a_section(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': self.section.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_instructor_cannot_delete_a_section_with_an_invalid_survey_pk(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': 100, 'section_pk': self.section.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_instructor_cannot_delete_a_section_with_an_invalid_section_pk(self):
        instructor = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Instructor,
        )
        instructor.save()
        url = reverse(
            'survey-section-detail', kwargs={'survey_pk': self.survey.id, 'section_pk': 100})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)


class StudentUpdateTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            andrew_id='testuser',
        )
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

        self.course = Course(
            course_number='12345',
            course_name='Test Course',
            syllabus='Test Syllabus',
            semester='Fall',
            visible=True,
        )
        self.course.save()

        self.survey = SurveyTemplate(
            name='Test Survey',
            instructions='Test Instructions',
            other_info='Test Other Info',
        )
        self.survey.save()

        self.section = SurveySection(
            template=self.survey,
            title='Test Section',
            description='Test Description',
            is_required=True,
        )
        self.section.save()

    def test_student_cannot_update_section(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()
        url = reverse(
            'section-detail', kwargs={'section_pk': self.section.id})
        data = {
            'title': 'Test Section 1 ',
            'description': 'Test Description 1 ',
            'is_required': 'true',
        }
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_update_question(self):
        student = Registration(
            users=self.user,
            courses=self.course,
            userRole=Registration.UserRole.Student,
        )
        student.save()

        question = Question(
            section=self.section,
            text='Test Question',
            question_type=Question.QuestionType.MULTIPLETEXT,
            is_required=True,
            is_multiple=True,
        )
        question.save()

        url = reverse(
            'question-detail', kwargs={'question_pk': question.pk})
        data = {
            'section': self.section,
            'text': 'Test Question failed',
            'question_type': Question.QuestionType.MULTIPLETEXT,
            'is_required': True,
            'is_multiple': True,
        }
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
