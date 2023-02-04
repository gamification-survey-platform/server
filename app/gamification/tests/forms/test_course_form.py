from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from app.gamification.forms import CourseForm


class CourseFormTest(TestCase):
    def test_empty_course_name_fails(self):
        data = {'course_name': '', 'course_number': '123'}
        form = CourseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('course_name', form.errors)

    def test_empty_course_number_fails(self):
        data = {'course_name': 'Test Course', 'course_number': ''}
        form = CourseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('course_number', form.errors)

    def test_upload_file_with_valid_extension(self):
        filename = 'app/gamification/tests/files/course_file.json'
        file = open(filename, 'rb')
        file = SimpleUploadedFile(filename, file.read())
        data = {'course_name': 'Test Course', 'course_number': '123'}
        form = CourseForm(data=data, files={'file': file})

        self.assertTrue(form.is_valid())

    def test_upload_file_with_invalid_extension(self):
        filename = 'app/gamification/tests/files/course_file.txt'
        file = open(filename, 'rb')
        file = SimpleUploadedFile(filename, file.read())
        data = {'course_name': 'Test Course', 'course_number': '123'}
        form = CourseForm(data=data, files={'file': file})

        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_upload_file_with_valid_format(self):
        filename = 'app/gamification/tests/files/course_file.json'
        file = open(filename, 'rb')
        file = SimpleUploadedFile(filename, file.read())
        data = {'course_name': 'Test Course', 'course_number': '123'}
        form = CourseForm(data=data, files={'file': file})

        self.assertTrue(form.is_valid())

    def test_upload_file_with_invalid_format(self):
        filename = 'app/gamification/tests/files/invalid_format.json'
        file = open(filename, 'rb')
        file = SimpleUploadedFile(filename, file.read())
        data = {'course_name': 'Test Course', 'course_number': '123'}
        form = CourseForm(data=data, files={'file': file})

        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
