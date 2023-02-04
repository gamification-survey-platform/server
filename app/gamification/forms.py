import json
from datetime import datetime
import pytz
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext, gettext_lazy as _
from app.gamification.models.survey_section import SurveySection

from app.gamification.models.survey_template import SurveyTemplate

from .models import Assignment, CustomUser, Course, Registration, Team, Membership, FeedbackSurvey, Question, Artifact, TodoList


class SignUpForm(forms.ModelForm):

    error_messages = {
        'password_mismatch': _("The two password fields didn't match.")
    }

    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Enter the same password as before, for verification'),
    )

    class Meta:
        model = CustomUser
        fields = ('andrew_id', 'email',)
        field_classes = {'andrew_id': auth_forms.UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super()
        password = self.cleaned_data.get('password1')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password1', error)

    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class PasswordResetForm(auth_forms.PasswordResetForm):
    error_messages = {
        'invalid_email': _("Email does not exist")
    }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        users = CustomUser.objects.filter(email=email)
        if len(users) <= 0:
            raise ValidationError(
                self.error_messages['invalid_email'],
            )

        return email


class ProfileForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'image')


class CourseForm(forms.ModelForm):

    error_messages = {
        'invalid_format': _('File format is not correct. Please check the file \
            format. Make sure that the file contains the following columns: \
            Student ID, Email, Team Name.'),
        'course_name_empty': _("Course name cannot be empty."),
        'course_number_empty': _("Course number cannot be empty."),
    }

    file = forms.FileField(
        label=_('CATME File'),
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['json'])],
        help_text=_('Upload a JSON file containing the team information.')
    )

    class Meta:
        model = Course
        fields = ('course_number', 'course_name', 'syllabus',
                  'semester', 'visible', 'picture')

    def clean_course_number(self):
        course_number = self.cleaned_data.get('course_number')
        if course_number == '':
            raise ValidationError(
                self.error_messages['course_number_empty'],
                code='course_number_empty',
            )
        return course_number

    def clean_course_name(self):
        course_name = self.cleaned_data.get('course_name')
        if course_name == '':
            raise ValidationError(
                self.error_messages['course_name_empty'],
                code='course_name_empty',
            )
        return course_name

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file is None:
            return file

        data = json.loads(file.read())
        for row in data:
            if 'Student ID' not in row or 'Email' not in row or 'Team Name' not in row:
                raise ValidationError(
                    self.error_messages['invalid_format'],
                    code='invalid_format'
                )

        file.seek(0)    # Reset file iterator

        return file

    def _register_teams(self, course):
        # Register teams from CATME file
        file = self.cleaned_data.get('file')
        if file is None:
            return

        data = json.loads(file.read())

        for row in data:
            name = row.get('Name', None).strip()
            andrew_id = row['Student ID'].strip()
            email = row['Email'].strip()
            team_name = row['Team Name'].strip()

            # Get user or create one
            try:
                user = CustomUser.objects.get(andrew_id=andrew_id)
            except CustomUser.DoesNotExist:
                if name:
                    last_name, first_name = name.split(', ')
                else:
                    first_name = last_name = ''
                user = CustomUser.objects.create_user(
                    andrew_id=andrew_id,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )

                password = CustomUser.objects.make_random_password()
                user.set_password(password)
                user.save()

            # Register this user to the course
            registration = Registration(
                users=user,
                courses=course,
                userRole=Registration.UserRole.Student
            )
            registration.save()

            # Do not create team if the name is empty
            if team_name == '':
                continue

            # Get team or create one
            try:
                team = Team.objects.get(course=course, name=team_name)
            except Team.DoesNotExist:
                team = Team(course=course, name=team_name)
                team.save()

            # Register this user to the team
            membership = Membership(student=registration, entity=team)
            membership.save()

        file.seek(0)    # Reset file iterator

    def save(self, commit=True):
        course = super().save(commit=True)
        self._register_teams(course)

        return course


class AssignmentForm(forms.ModelForm):

    class Meta:
        model = Assignment
        fields = ('course', 'assignment_name', 'description',
                  'assignment_type', 'submission_type', 'total_score',
                  'date_created', 'date_released', 'date_due')
        widgets = {
            # 'course': forms.TextInput(attrs={'readonly': 'readonly'}),
            'course': forms.HiddenInput(),
        }


class AddSurveyForm(forms.ModelForm):

    class Meta:
        model = FeedbackSurvey
        fields = ('template', 'assignment', 'date_due',
                  'date_released')
        widgets = {
            'assignment': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class ArtifactForm(forms.ModelForm):

    class Meta:
        model = Artifact
        fields = ('entity', 'assignment', 'upload_time', 'file')
        widgets = {
            # TODO: solve display issue
            # 'entity': forms.Select(attrs={'readonly': 'readonly'}),
            'entity': forms.HiddenInput(),
            # 'assignment': forms.Select(attrs={'readonly': 'readonly'}),
            'assignment': forms.HiddenInput(),
            'upload_time': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def save(self, commit=True):
        artifact = super().save(commit=False)
        artifact.upload_time = datetime.now().astimezone(
            pytz.timezone('America/Los_Angeles'))
        artifact.save()
        return artifact


class TodoListForm(forms.ModelForm):

    class Meta:
        model = TodoList
        fields = ('user', 'text', 'due_date',
                  'type_name', 'type_icon', 'mandatory')
        widhets = {
            # 'user': forms.HiddenInput(),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
