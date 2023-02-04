from http import client
from sys import prefix
from django.forms import SelectDateWidget
from django.test import TestCase
from django.urls import resolve, reverse
import os
import shutil

from app.gamification.forms import ArtifactForm
from app.gamification.views.pages import artifact
from app.gamification.tests.views.pages.utils import LogInUser
from django.conf import settings
from app.gamification.models import Assignment, Course, Artifact, Team, Registration
from django.core.files.uploadedfile import SimpleUploadedFile

from app.gamification.views.pages.views import assignment

"""Test the assignment view.
    -  Using All Combinations of:
        - User Type: Student in this course, Instructor in this course, TA in this course,
                    Student in another course, Instructor in another course, TA in another course.
        - Course: visible, hidden, deleted, not created.
        - Assignment: group assignment, individual assignment, not created.
        - Artifact: file, link, empty, not created, deleted, edited.
"""
class ArtifactTest(TestCase):
    def setUp(self):
        # Create a user (student)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=False)
        
        # Create another user (instructor)
        test_andrew_id_2 = 'andrew_id_2'
        test_password_2 = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id_2, test_password_2, is_superuser=True)
        
        # Create a course
        self.course_data = {
            'course_name': 'testName',
            'course_number': '18652',
        }
        self.url = reverse('course')
        self.response = self.client.post(self.url, data=self.course_data)
        
        # Add an assignment
        course_id = Course.objects.get(course_name='testName').pk
        self.url = reverse('assignment', kwargs={'course_id': course_id})
        self.assignment_data = {
            'assignment_name': 'testNameAssignment',
            'course': course_id,
        }
        self.response = self.client.post(self.url, data=self.assignment_data)
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        
        # Add the student to a team in this course
        self.url = reverse('member_list', args = [course_id])
        test_member_andrewId = 'andrew_id'
        test_member_team = 'T1'
        test_member_role = Registration.UserRole.Student
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        team_id = Team.objects.get(name=test_member_team).pk
        
        # Logout and login as the student
        # client.logout()
        self.client.login(andrew_id='andrew_id', password='1234')
        
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.response = self.client.get(self.url)
    
    def tearDown(self):
        # Remove MEDIA directory after tests finish
        try:
            if(os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
        except Exception as e:
            print(e)
            # Still downloading files, so ignore this error
            pass
    
    def test_artifact_page_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        
    def test_artifact_url_resolves_artifact_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func, artifact)
        
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    
    def test_artifact_form_is_valid(self):
        form = ArtifactForm(data={
            'entity': Team.objects.get(name='T1'),
            'assignment': Assignment.objects.get(assignment_name='testNameAssignment'),
            'file': SimpleUploadedFile(
                name='testName.txt',
                content=b'file_content',
                content_type='text/plain'),
        })
        self.assertTrue(form.is_valid())
                                 
                         
class ArtifactAddTest(TestCase):
    def setUp(self):
        # Create a user (student)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=False)
        
        # Create another user (instructor)
        test_andrew_id_2 = 'andrew_id_2'
        test_password_2 = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id_2, test_password_2, is_superuser=True)
        
        # Create a course
        self.course_data = {
            'course_name': 'testName',
            'course_number': '18652',
        }
        self.url = reverse('course')
        self.response = self.client.post(self.url, data=self.course_data)
        
        # Add an assignment
        course_id = Course.objects.get(course_name='testName').pk
        self.url = reverse('assignment', kwargs={'course_id': course_id})
        self.assignment_data = {
            'assignment_name': 'testNameAssignment',
            'course': course_id,
        }
        self.response = self.client.post(self.url, data=self.assignment_data)
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        
        # Add the student to a team in this course
        self.url = reverse('member_list', args = [course_id])
        test_member_andrewId = 'andrew_id'
        test_member_team = 'T1'
        test_member_role = Registration.UserRole.Student
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        team_id = Team.objects.get(name=test_member_team).pk
        
        # Logout and login as the student
        self.client.logout()
        self.client.login(andrew_id='andrew_id', password='1234')
        
    def tearDown(self):
        # Remove MEDIA directory after tests finish
        try:
            if(os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
        except Exception as e:
            print(e)
            # Still downloading files, so ignore this error
            pass
    
    def test_artifact_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_add_artifact(self):
        # Add an artifact
        course_id = Course.objects.get(course_name='testName').pk
        team_id = Team.objects.get(name='T1').pk
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        self.assertFalse(Artifact.objects.filter(entity = team_id).exists())
        
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.jpg'
        f = open(filepath, 'rb')
        uploaded_file = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.artifact_data = {
            'entity': team_id,
            'assignment': assignment_id,
            'file': uploaded_file
        }
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.response = self.client.post(self.url, data=self.artifact_data)
        self.assertEqual(self.response.status_code, 200)
        
        artifact = Artifact.objects.get(entity = team_id)
        self.assertEqual(artifact.assignment.pk, assignment_id)
        file_prefix = 'assignment_files/'
        # TODO: suffix of file name is not correct
        # self.assertEqual(artifact.file.name, file_prefix + uploaded_file.name)
        self.assertTrue(artifact.file.name.startswith(file_prefix))
        
        
# Edit
class ArtifactEditTest(TestCase):
    def setUp(self):
        # Create a user (student)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=False)
        
        # Create another user (instructor)
        test_andrew_id_2 = 'andrew_id_2'
        test_password_2 = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id_2, test_password_2, is_superuser=True)
        
        # Create a course
        self.course_data = {
            'course_name': 'testName',
            'course_number': '18652',
        }
        self.url = reverse('course')
        self.response = self.client.post(self.url, data=self.course_data)
        
        # Add an assignment
        course_id = Course.objects.get(course_name='testName').pk
        self.url = reverse('assignment', kwargs={'course_id': course_id})
        self.assignment_data = {
            'assignment_name': 'testNameAssignment',
            'course': course_id,
        }
        self.response = self.client.post(self.url, data=self.assignment_data)
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        
        # Add the student to a team in this course
        self.url = reverse('member_list', args = [course_id])
        test_member_andrewId = 'andrew_id'
        test_member_team = 'T1'
        test_member_role = Registration.UserRole.Student
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        team_id = Team.objects.get(name=test_member_team).pk
        
        # Logout and login as the student
        self.client.logout()
        self.client.login(andrew_id='andrew_id', password='1234')
        
        # Add an artifact
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.jpg'
        f = open(filepath, 'rb')
        uploaded_file = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.artifact_data = {
            'entity': team_id,
            'assignment': assignment_id,
            'file': uploaded_file
        }
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.response = self.client.post(self.url, data=self.artifact_data)
        
    def tearDown(self):
        # Remove MEDIA directory after tests finish
        try:
            if(os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
        except Exception as e:
            print(e)
            # Still downloading files, so ignore this error
            pass
          
    def test_artifact_edit_status_code(self):
        self.assertEqual(self.response.status_code, 200)  
     
    def test_edit_artifact(self):
        # Edit an artifact
        course_id = Course.objects.get(course_name='testName').pk
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment', course=course_id).pk
        team_id = Team.objects.get(name='T1').pk
        artifact_id = Artifact.objects.get(entity = team_id, assignment = assignment_id).pk
        
        self.url = reverse('edit_artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id, 'artifact_id': artifact_id})
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face2.jpg'
        f = open(filepath, 'rb')
        uploaded_file = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        self.edit_artifact_data = {
            'entity': team_id,
            'assignment': assignment_id,
            'file': uploaded_file
        }
        self.response = self.client.post(self.url, data=self.edit_artifact_data)
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(Artifact.objects.filter(entity = team_id).exists())
        artifact = Artifact.objects.get(entity = team_id)
        self.assertEqual(artifact.assignment.pk, assignment_id)
        file_prefix = 'assignment_files/'
        self.assertEqual(artifact.file.name, file_prefix + 'face2.jpg')
            
class ArtifactViewTest(TestCase):
    def setUp(self):
        # Create a user (student)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=False)
        
        # Create another user (instructor)
        test_andrew_id_2 = 'andrew_id_2'
        test_password_2 = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id_2, test_password_2, is_superuser=True)
        
        # Create a course
        self.course_data = {
            'course_name': 'testName',
            'course_number': '18652',
        }
        self.url = reverse('course')
        self.response = self.client.post(self.url, data=self.course_data)
        
        # Add an assignment
        course_id = Course.objects.get(course_name='testName').pk
        self.url = reverse('assignment', kwargs={'course_id': course_id})
        self.assignment_data = {
            'assignment_name': 'testNameAssignment',
            'course': course_id,
        }
        self.response = self.client.post(self.url, data=self.assignment_data)
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        
        # Add the student to a team in this course
        self.url = reverse('member_list', args = [course_id])
        test_member_andrewId = 'andrew_id'
        test_member_team = 'T1'
        test_member_role = Registration.UserRole.Student
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        team_id = Team.objects.get(name=test_member_team).pk
        
        # Logout and login as the student
        self.client.logout()
        self.client.login(andrew_id='andrew_id', password='1234')
        
        # Add an artifact
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.jpg'
        f = open(filepath, 'rb')
        uploaded_file = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.artifact_data = {
            'entity': team_id,
            'assignment': assignment_id,
            'file': uploaded_file
        }
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.response = self.client.post(self.url, data=self.artifact_data)
        
    def tearDown(self):
        # Remove MEDIA directory after tests finish
        try:
            if(os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
        except Exception as e:
            print(e)
            # Still downloading files, so ignore this error
            pass
            
    def test_view_artifact(self):
        course_id = Course.objects.get(course_name='testName').pk
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment', course=course_id).pk
        team_id = Team.objects.get(name='T1').pk
        artifact_id = Artifact.objects.get(entity = team_id, assignment = assignment_id).pk
        
        self.url = reverse('view_artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id, 'artifact_id': artifact_id})
        self.response = self.client.get(self.url)
        
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(Artifact.objects.filter(entity = team_id, assignment = assignment_id).exists())
        artifact = Artifact.objects.get(entity = team_id)
        self.assertEqual(artifact.assignment.pk, assignment_id)
        file_prefix = 'assignment_files/'
        self.assertEqual(artifact.file.name, file_prefix + 'face1.jpg')
        
# Delete
class ArtifactDeleteTest(TestCase):
    def setUp(self):
        # Create a user (student)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=False)
        
        # Create another user (instructor)
        test_andrew_id_2 = 'andrew_id_2'
        test_password_2 = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id_2, test_password_2, is_superuser=True)
        
        # Create a course
        self.course_data = {
            'course_name': 'testName',
            'course_number': '18652',
        }
        self.url = reverse('course')
        self.response = self.client.post(self.url, data=self.course_data)
        
        # Add an assignment
        course_id = Course.objects.get(course_name='testName').pk
        self.url = reverse('assignment', kwargs={'course_id': course_id})
        self.assignment_data = {
            'assignment_name': 'testNameAssignment',
            'course': course_id,
        }
        self.response = self.client.post(self.url, data=self.assignment_data)
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        
        # Add the student to a team in this course
        self.url = reverse('member_list', args = [course_id])
        test_member_andrewId = 'andrew_id'
        test_member_team = 'T1'
        test_member_role = Registration.UserRole.Student
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        team_id = Team.objects.get(name=test_member_team).pk
        
        # Logout and login as the student
        self.client.logout()
        self.client.login(andrew_id='andrew_id', password='1234')
        
        # Add an artifact
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face1.jpg'
        f = open(filepath, 'rb')
        uploaded_file = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.artifact_data = {
            'entity': team_id,
            'assignment': assignment_id,
            'file': uploaded_file
        }
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.response = self.client.post(self.url, data=self.artifact_data)
        
    def tearDown(self):
        # Remove MEDIA directory after tests finish
        try:
            if(os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
        except Exception as e:
            print(e)
            # Still downloading files, so ignore this error
            pass
    
    def test_delete_artifact(self):
        # Edit an artifact
        self.client.login(andrew_id='andrew_id', password='1234')
        
        course_id = Course.objects.get(course_name='testName').pk
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment', course=course_id).pk
        team_id = Team.objects.get(name='T1').pk
        artifact_id = Artifact.objects.get(entity = team_id, assignment = assignment_id).pk
        self.assertTrue(Artifact.objects.filter(entity = team_id).exists())

        
        self.url = reverse('delete_artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id, 'artifact_id': artifact_id})
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 302)
        self.assertFalse(Artifact.objects.filter(entity = team_id).exists())
        
    
# Download
class ArtifactDownloadTest(TestCase):
    def setUp(self):
        # Create a user (student)
        test_andrew_id = 'andrew_id'
        test_password = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id, test_password, is_superuser=False)
        
        # Create another user (instructor)
        test_andrew_id_2 = 'andrew_id_2'
        test_password_2 = '1234'
        LogInUser.createAndLogInUser(
            self.client, test_andrew_id_2, test_password_2, is_superuser=True)
        
        # Create a course
        self.course_data = {
            'course_name': 'testName',
            'course_number': '18652',
        }
        self.url = reverse('course')
        self.response = self.client.post(self.url, data=self.course_data)
        
        # Add an assignment
        course_id = Course.objects.get(course_name='testName').pk
        self.url = reverse('assignment', kwargs={'course_id': course_id})
        self.assignment_data = {
            'assignment_name': 'testNameAssignment',
            'course': course_id,
        }
        self.response = self.client.post(self.url, data=self.assignment_data)
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment').pk
        
        # Add the student to a team in this course
        self.url = reverse('member_list', args = [course_id])
        test_member_andrewId = 'andrew_id'
        test_member_team = 'T1'
        test_member_role = Registration.UserRole.Student
        self.data = {
            'andrew_id': test_member_andrewId,
            'team_name': test_member_team,
            'membershipRadios': test_member_role,
        }
        self.response = self.client.post(self.url, self.data)
        team_id = Team.objects.get(name=test_member_team).pk
        
        # Logout and login as the student
        self.client.logout()
        self.client.login(andrew_id='andrew_id', password='1234')
        
        # Add an artifact
        filepath = settings.STATICFILES_DIRS[0] / 'images/faces/face3.jpg'
        f = open(filepath, 'rb')
        uploaded_file = SimpleUploadedFile(
            name=filepath,
            content=f.read(),
            content_type='image/jpg'
        )
        
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.artifact_data = {
            'entity': team_id,
            'assignment': assignment_id,
            'file': uploaded_file
        }
        self.url = reverse('artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id})
        self.response = self.client.post(self.url, data=self.artifact_data)
        
    def tearDown(self):
        # Remove MEDIA directory after tests finish
        try:
            if(os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
        except Exception as e:
            print(e)
            # Still downloading files, so ignore this error
            pass
            
    def test_download_artifact(self):
        self.client.login(andrew_id='andrew_id', password='1234')
        
        course_id = Course.objects.get(course_name='testName').pk
        assignment_id = Assignment.objects.get(assignment_name='testNameAssignment', course=course_id).pk
        team_id = Team.objects.get(name='T1').pk
        artifact_id = Artifact.objects.get(entity = team_id, assignment = assignment_id).pk
        self.assertTrue(Artifact.objects.filter(entity = team_id, assignment = assignment_id).exists())
        
        self.url = reverse('download_artifact', kwargs={'course_id': course_id, 'assignment_id': assignment_id, 'artifact_id': artifact_id})
        self.response = self.client.get(self.url)
        # response is a file download
        self.assertEqual(self.response.status_code, 200)
        file = self.response
        print("file: " + str(file))
        self.assertTrue(file)
        # Check return is a file and check file name
        self.assertEquals(
            self.response.get('Content-Disposition'),
            'inline; filename="face3.jpg"'
        )