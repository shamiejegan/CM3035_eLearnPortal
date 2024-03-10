from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone


from .model_factories import * 
from ..forms import *

# TESTS FORMS
################

class UserFormTest(TestCase):
    def test_valid_email(self):
        form = UserForm(data={
            'email': 'test@example.com',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_email_as_word(self):
        form = UserForm(data={
            'email': 'notanemail',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_email_no_tld(self):
        form = UserForm(data={
            'email': 'test@example',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    def test_invalid_email_startswith_at(self):
        form = UserForm(data={
            'email': '@example.com',
            'password': 'securepassword123',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)        


class UpdateStatusFormTest(TestCase):
    def test_form_with_no_status(self):
        form_data = {}
        form = UpdateStatusForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_status(self):
        form_data = {'status': 'Busy'}
        form = UpdateStatusForm(data=form_data)
        self.assertTrue(form.is_valid())



class CourseFormTest(TestCase):
    def setUp(self):
        Course.objects.create(module_code="AB1234", title="Sample Course")

    def test_valid_course_form_unique_is_valid(self):
        form_data = {'module_code': 'CS2020', 'title': 'New Course'}
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_module_code_wrong_module_code_format_words_invalid(self):
        form_data = {'module_code': 'WrongFormat', 'title': 'Another Course'}
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_module_code_wrong_module_code_format_numbers_invalid(self):
        form_data = {'module_code': '012345', 'title': 'Another Course'}
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_duplicate_module_code_duplicated_invalid(self):
        form_data = {'module_code': 'AB1234', 'title': 'Duplicate Course'}
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())

class MaterialFormTest(TestCase):
    def test_file_size_under_limit_valid(self):
        small_file = SimpleUploadedFile("small_file.txt", b"Hello World")
        form = MaterialForm(data={'title': 'Small File'}, files={'file': small_file})
        if form.errors:
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_file_size_over_limit_invalid(self):
        # Generating a file larger than 10MB
        large_file = SimpleUploadedFile("large_file.txt", b"x" * (10 * 1024 * 1024 + 1))
        form_data = {'title': 'Large File', 'file': large_file}
        form = MaterialForm(data=form_data)
        self.assertFalse(form.is_valid())

class AssignmentFormTest(TestCase):
    def test_deadline_in_future_is_valid(self):
        form_data = {
            'title': 'Future Assignment',
            'startdate': timezone.now(),
            'deadline': timezone.now() + timezone.timedelta(days=1)
        }
        form = AssignmentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_deadline_in_past_is_invalid(self):
        form_data = {
            'title': 'Past Assignment',
            'startdate': timezone.now(),
            'deadline': timezone.now() - timezone.timedelta(days=1)
        }
        form = AssignmentForm(data=form_data)
        self.assertFalse(form.is_valid())
