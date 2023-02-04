from django import forms
from django.test import TestCase

from app.gamification.templatetags.form_tags import field_type, input_class, input_style


class ExampleForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    is_staff = forms.BooleanField()
    date = forms.DateField()
    datetime = forms.DateTimeField()
    choices = forms.ChoiceField(choices=[('1', 'One'), ('2', 'Two')])

    class Meta:
        fields = ('name', 'password', 'is_staff',
                  'date', 'datetime', 'choices')


class FieldTypeTests(TestCase):
    def test_field_widget_type(self):
        form = ExampleForm()
        self.assertEqual('TextInput', field_type(form['name']))
        self.assertEqual('PasswordInput', field_type(form['password']))
        self.assertEqual('CheckboxInput', field_type(form['is_staff']))
        self.assertEqual('DateInput', field_type(form['date']))
        self.assertEqual('DateTimeInput', field_type(form['datetime']))
        self.assertEqual('Select', field_type(form['choices']))


class InputClassTests(TestCase):
    def test_unbound_field_initial_state(self):
        form = ExampleForm()  # unbound form
        self.assertEquals('form-control', input_class(form['name']))
        self.assertEquals('form-control', input_class(form['password']))
        self.assertEquals('form-check-input', input_class(form['is_staff']))
        self.assertEquals('form-control datepicker', input_class(form['date']))
        self.assertEquals('form-control datetimepicker',
                          input_class(form['datetime']))
        self.assertEquals('form-control', input_class(form['choices']))

    def test_valid_bound_field(self):
        # bound form (field + data)
        form = ExampleForm({'name': 'john', 'password': '123'})
        self.assertEquals('form-control is-valid', input_class(form['name']))
        self.assertEquals('form-control', input_class(form['password']))

    def test_invalid_bound_field(self):
        # bound form (field + data)
        form = ExampleForm({'name': '', 'password': '123'})
        self.assertEquals('form-control is-invalid', input_class(form['name']))
        self.assertEquals('form-control', input_class(form['password']))


class InputStyleTests(TestCase):
    def test_field_style(self):
        form = ExampleForm()
        self.assertEquals(
            'height: auto; padding: 0.375rem 0.75rem;',
            input_style(form['name']))
        self.assertEquals('', input_style(form['is_staff']))
        self.assertEquals(
            'height: auto; padding: 0.375rem 0.75rem; color: #212529;',
            input_style(form['choices']))
