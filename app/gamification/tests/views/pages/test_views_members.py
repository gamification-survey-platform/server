from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from app.gamification.models import CustomUser, Course, Registration
from app.gamification.models.entity import Team
from app.gamification.models.membership import Membership
from app.gamification.tests.views.pages.utils import LogInUser 

"""Test the assignment view.
    -  Using All Combinations of:
        - User Type: Student in this course, Instructor in this course, TA in this course,
                    Student in another course, Instructor in another course, TA in another course.
        - Course: visible, hidden, deleted, not created.
        - Assignment: group assignment, individual assignment, not created.
"""

class GetMemberTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json', 'membership.json', 'entities.json']

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

        self.invisible_course = Course.objects.get(
            course_number='18749', semester='Summer 2024')
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021'
        )

        self.student = CustomUser.objects.get(
            andrew_id=self.student_andrew_id)  # pk = 3
        self.ta = CustomUser.objects.get(andrew_id=self.ta_andrew_id)
        self.instructor = CustomUser.objects.get(
            andrew_id=self.instructor_andrew_id)
        self.admin = CustomUser.objects.get(andrew_id=self.admin_andrew_id)
    
    def test_get_member(self):
        ENROLLED_COURSE = 1
        STUDENT_TEAM = 'T1'
        STUDENT_USERROLE = 'Student'
        EMPTY_TEAM = ''
        TA_USERROLE = 'TA'
        INSTRUCTOR_USERROLE = 'Instructor'
        self.client.login(
            andrew_id=self.student_andrew_id,
            password=self.student_password,
        )
        self.url = reverse('member_list', args = [ENROLLED_COURSE])
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        membership = self.response.context.get('membership')
        andrew_id = [
            i['andrew_id'] for i in membership]
        team = [
            i['team'] for i in membership]
        userRole = [
            i['userRole'] for i in membership]    
        
        # Student in member list
        self.assertIn(self.student_andrew_id, andrew_id)
        student_index = andrew_id.index(self.student_andrew_id)
        self.assertEqual(team[student_index], STUDENT_TEAM)
        self.assertEqual(userRole[student_index], STUDENT_USERROLE)
        
        # TA in member list
        self.assertIn(self.ta_andrew_id, andrew_id)
        ta_index = andrew_id.index(self.ta_andrew_id)
        self.assertEqual(team[ta_index], EMPTY_TEAM)
        self.assertEqual(userRole[ta_index], TA_USERROLE)

        # Instructor in member list
        self.assertIn(self.instructor_andrew_id, andrew_id)
        instructor_index = andrew_id.index(self.instructor_andrew_id)
        self.assertEqual(team[instructor_index], EMPTY_TEAM)
        self.assertEqual(userRole[instructor_index], INSTRUCTOR_USERROLE)


class AddMemberTest(TestCase):
    def setUp(self):
        LogInUser.createAndLogInUser(
            self.client, 'exist_id', '123', is_superuser=False)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=True)
        self.url = reverse('course')
        self.client.get(self.url)
        test_course_name = "course1"
        test_course_number = "123"
        self.data = {
            'course_name': test_course_name,
            'course_number': test_course_number,
        }
        self.response = self.client.post(self.url, self.data)
        self.course_pk = self.response.context.get('registration')[0].courses.pk

    def test_add_member(self):
        self.url = reverse('member_list', args = [self.course_pk])
        test_member_andrewId = 'exist_id'
        test_member_team = 'T1'
        test_member_role = 'Student'
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context.get('membership')[1]['andrew_id'], test_member_andrewId)
        self.assertEqual(self.response.context.get('membership')[1]['userRole'], test_member_role)
        self.assertEqual(self.response.context.get('membership')[1]['team'], test_member_team)
    
    def test_add_inexistent_member(self):
        self.url = reverse('member_list', args = [self.course_pk])
        test_member_andrewId = 'not_exist_id'
        test_member_team = 'T1'
        test_member_role = 'Student'
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        self.assertEqual(self.response.status_code, 200)
        # TODO: Fix this test
        # self.assertEqual(self.response.context.get('membership'), [{'andrew_id': 'andrew_id', 'userRole': 'Instructor', 'team': ''}])
        self.assertEqual(list(get_messages(self.response.wsgi_request))[0].message, 'AndrewID does not exist')
    
    def test_add_member_without_team(self):
        #andrewID, Role, Team
        self.url = reverse('member_list', args = [self.course_pk])
        test_member_andrewId = 'exist_id'
        test_member_team = ''
        test_member_role = 'Student'
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(get_messages(self.response.wsgi_request))[0].message, 'A new member has been added')
        self.assertEqual(self.response.context.get('membership')[1]['andrew_id'], test_member_andrewId)
        self.assertEqual(self.response.context.get('membership')[1]['userRole'], test_member_role)
        self.assertEqual(self.response.context.get('membership')[1]['team'], test_member_team)

    def test_add_team_without_andrewID(self):
        #andrewID, Role, Team
        self.url = reverse('member_list', args = [self.course_pk])
        test_member_andrewId = ''
        test_member_team = 'T1'
        test_member_role = 'Student'
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        self.assertEqual(list(get_messages(self.response.wsgi_request))[0].message, 'AndrewID does not exist')

class AddMemberPermissionTest(TestCase):

    fixtures = ['users.json', 'courses.json', 'registration.json', 'membership.json', 'entities.json']

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

        self.invisible_course = Course.objects.get(
            course_number='18749', semester='Summer 2024')
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021'
        )

        self.student = CustomUser.objects.get(
            andrew_id=self.student_andrew_id)  # pk = 3
        self.ta = CustomUser.objects.get(andrew_id=self.ta_andrew_id)
        self.instructor = CustomUser.objects.get(
            andrew_id=self.instructor_andrew_id)
        self.admin = CustomUser.objects.get(andrew_id=self.admin_andrew_id)

    def test_user_not_in_this_course_cannot_add_member(self):
        course = Course.objects.filter(course_number='18749').first()
        self.client.login(username=self.student_andrew_id, password=self.student_password)
        url = reverse('member_list', args=[course.pk])
        data = {
            'andrew_id': 'user2',
            'team_name': 'T1',
            'membershipRadios': 'Student',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_add_member(self):
        self.client.login(username=self.student_andrew_id, password=self.student_password)
        url = reverse('member_list', args=[self.course.pk])

        test_member_andrewId = 'Andrew_id'
        test_member_team = 'T1'
        test_member_role = 'Student'
        data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }

        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('member_list', args = [self.course.pk]))
    
    def test_TA_can_add_member(self):
        self.client.login(username=self.ta_andrew_id, password=self.ta_password)
        url = reverse('member_list', args=[self.course.pk])

        test_member_andrewId = 'user2'
        test_member_team = 'Team1'
        test_member_role = 'Student'
        data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        user = CustomUser.objects.get(andrew_id=test_member_andrewId)

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(test_member_andrewId, list(get_messages(response.wsgi_request))[0].message)

        team = Team.objects.filter(name=test_member_team).first()
        registration = Registration.objects.filter(
            users__andrew_id=test_member_andrewId, courses=self.course).first()
        membership = Membership.objects.filter(
            entity=team, student=registration).first()
        self.assertIn(user, team.members)

    def test_instructor_can_add_member(self):
        self.client.login(username=self.instructor_andrew_id, password=self.instructor_password)
        url = reverse('member_list', args=[self.course.pk])

        test_member_andrewId = 'user2'
        test_member_team = 'Team1'
        test_member_role = 'Student'
        data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        user = CustomUser.objects.get(andrew_id=test_member_andrewId)

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(test_member_andrewId, list(get_messages(response.wsgi_request))[0].message)

        team = Team.objects.filter(name=test_member_team).first()
        registration = Registration.objects.filter(
            users__andrew_id=test_member_andrewId, courses=self.course).first()
        membership = Membership.objects.filter(
            entity=team, student=registration).first()
        self.assertIn(user, team.members)


class EditMemberTest(TestCase):
    fixtures = ['users.json', 'courses.json', 'registration.json', 'membership.json', 'entities.json']

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

        self.invisible_course = Course.objects.get(
            course_number='18749', semester='Summer 2024')
        self.course = Course.objects.get(
            course_number='18652', semester='Fall 2021'
        )

        self.student = CustomUser.objects.get(
            andrew_id=self.student_andrew_id)  # pk = 3
        self.ta = CustomUser.objects.get(andrew_id=self.ta_andrew_id)
        self.instructor = CustomUser.objects.get(
            andrew_id=self.instructor_andrew_id)
        self.admin = CustomUser.objects.get(andrew_id=self.admin_andrew_id)

    def test_add_student_to_an_existing_team(self):
        '''
        Test that a student can be added to an existing team
        '''
        NEW_TEAM = 'T2'
        self.client.login(
            andrew_id=self.ta_andrew_id,
            password=self.ta_password,
        )
        self.url = reverse('member_list', args = [self.course.pk])
        self.data = {
            'andrew_id': self.student_andrew_id,
            'team_name': NEW_TEAM,
            'membershipRadios': Registration.UserRole.Student,
        }
        self.response = self.client.post(self.url, self.data)
        team = Team.objects.get(course=self.course, name=NEW_TEAM)
        members = [i.andrew_id for i in team.members]
        self.assertIn(self.student_andrew_id, members)
        self.assertEqual(2, len(members))

    def test_add_student_to_a_non_existing_team(self):
        '''
        Test that a student can be added to a team that does not exist, and that
        the team is created.
        '''
        NEW_TEAM = 'T3'
        self.client.login(
            andrew_id=self.ta_andrew_id,
            password=self.ta_password,
        )
        self.url = reverse('member_list', args = [self.course.pk])
        self.data = {
            'andrew_id': self.student_andrew_id,
            'team_name': NEW_TEAM,
            'membershipRadios': Registration.UserRole.Student,
        }
        self.response = self.client.post(self.url, self.data)
        team = Team.objects.get(course=self.course, name=NEW_TEAM)
        members = [i.andrew_id for i in team.members]
        self.assertIn(self.student_andrew_id, members)
        self.assertEqual(1, len(members))

    def test_add_TA_to_an_existing_team(self):
        '''
        Test that a TA can be added to an existing team.
        '''
        NEW_TEAM = 'T2'
        self.client.login(
            andrew_id=self.ta_andrew_id,
            password=self.ta_password,
        )
        self.url = reverse('member_list', args = [self.course.pk])
        self.data = {
            'andrew_id': self.student_andrew_id,
            'team_name': NEW_TEAM,
            'membershipRadios': Registration.UserRole.TA,
        }
        self.response = self.client.post(self.url, self.data)
        team = Team.objects.get(course=self.course, name=NEW_TEAM)
        members = [i.andrew_id for i in team.members]
        self.assertNotIn(self.student_andrew_id, members)
        self.assertEqual(1, len(members))

    def test_update_user_role(self):
        '''
        Test that the user role is updated when the user is added to an existing team.
        '''
        NEW_TEAM = 'T2'
        self.client.login(
            andrew_id=self.ta_andrew_id,
            password=self.ta_password,
        )
        self.url = reverse('member_list', args = [self.course.pk])
        self.data = {
            'andrew_id': self.ta_andrew_id,
            'team_name': NEW_TEAM,
            'membershipRadios': Registration.UserRole.Student,
        }
        self.response = self.client.post(self.url, self.data)
        team = Team.objects.get(course=self.course, name=NEW_TEAM)
        members = [i.andrew_id for i in team.members]
        userRole = Registration.objects.get(users=self.ta, courses=self.course).userRole
        self.assertEqual(Registration.UserRole.Student, userRole)
        self.assertIn(self.ta_andrew_id, members)
        self.assertEqual(2, len(members))

    def test_membership_will_be_deleted_after_role_changed(self):
        '''
        Test that the membership will be deleted after the user role is changed
        from Student to TA/Instructor.
        '''
        NEW_TEAM = 'T2'
        self.client.login(
            andrew_id=self.ta_andrew_id,
            password=self.ta_password,
        )
        self.url = reverse('member_list', args = [self.course.pk])
        self.data = {
            'andrew_id': self.student_andrew_id,
            'team_name': NEW_TEAM,
            'membershipRadios': Registration.UserRole.TA,
        }
        self.response = self.client.post(self.url, self.data)
        registration = Registration.objects.get(users=self.student, courses=self.course)
        team = Team.objects.get(course=self.course, name=NEW_TEAM)
        membership = Membership.objects.filter(entity=team, student=registration)
        self.assertEqual(0, len(membership))
        members = [i.andrew_id for i in team.members]
        self.assertNotIn(self.student_andrew_id, members)
        andrew_id = [i.registration.users.andrew_id for i in membership]
        self.assertNotIn(self.student_andrew_id, andrew_id)


class DeleteMemberTest(TestCase):
    def setUp(self):
        LogInUser.createAndLogInUser(
            self.client, 'exist_id', '123', is_superuser=False)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=True)
        self.url = reverse('course')
        self.client.get(self.url)
        test_course_name = "course1"
        test_course_number = "123"
        self.data = {
            'course_name': test_course_name,
            'course_number': test_course_number,
        }
        self.response = self.client.post(self.url, self.data)
        self.course = self.response.context.get('registration')[0].courses
        self.course_pk = self.course.pk
        self.url = reverse('member_list', args = [self.course_pk])
        self.test_member_andrewId = 'exist_id'
        self.test_member_team = 'T1'
        self.test_member_role = 'Student'
        self.data = {
            'andrew_id': self.test_member_andrewId,
            'team_name': self.test_member_team,
            'membershipRadios': self.test_member_role,
        }
        self.client.post(self.url, self.data)

    def test_delete_member(self):
        user = CustomUser.objects.get(andrew_id='exist_id')
        registration = Registration.objects.get(users=user, courses=self.course)
        team = Team.objects.get(course=self.course, name=self.test_member_team)
        membership = Membership.objects.filter(entity=team, student=registration)

        self.url = reverse('delete_member', args = [self.course_pk, 'exist_id'])
        self.client.get(self.url)
        registratiton = Registration.objects.all()

        self.assertEqual(0, len(membership))
        self.assertEqual(1, len(registratiton))

    def test_deletet_not_existing_member(self):
        NOT_EXISTING_USER = 'user5'
        self.url = reverse('delete_member', args = [self.course_pk, NOT_EXISTING_USER])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
    
    def test_student_cannot_delete_member(self):
        user = CustomUser.objects.get(andrew_id='exist_id')
        registration = Registration.objects.get(users=user, courses=self.course, userRole=Registration.UserRole.Student)
        team = Team.objects.get(course=self.course, name=self.test_member_team)
        membership = Membership.objects.filter(entity=team, student=registration)

        self.client.login(andrew_id='exist_id', password='123')

        self.url = reverse('delete_member', args = [self.course_pk, 'exist_id'])
        self.client.get(self.url)
        registratiton = Registration.objects.all()

        self.assertEqual(2, len(registratiton))
        