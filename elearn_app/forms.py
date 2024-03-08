from django import forms
from django.forms import ModelForm
from .models import * 
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserForm(ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = ['photo']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # photo is optional
        self.fields['photo'].required = False  

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['is_student'] = 'True'
        cleaned_data['is_instructor'] = 'False'
        return cleaned_data

class UpdateStatusForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(UpdateStatusForm, self).__init__(*args, **kwargs)
        # status is optional
        self.fields['status'].required = False 

class CourseForm(forms.ModelForm):
    instructor = User.username

    class Meta:
        model = Course
        fields = ['module_code', 'title', 'students']

    # ensure that module_code does not already exist
    def clean_module_code(self):
        module_code = self.cleaned_data['module_code']

        # Set regex validator to only accept values in fromat of two capital letters followed by four digits. Assign message if invalid
        regex_validator = RegexValidator(
            regex=r'^[A-Z]{2}\d{4}$',
            message="Invalid module code format. Module code should be two capital letters followed by four digits. Example: AB1234"
        )
        regex_validator(module_code)  
        
        # check if module_code already exists
        if Course.objects.filter(module_code=module_code).exists():
            raise forms.ValidationError("Module code already exists")
        
        return module_code

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'file']

# https://pypi.org/project/django-bootstrap-datepicker-plus/
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'startdate', 'deadline']
        widgets = {
            'startdate': DateTimePickerInput(),
            'deadline': DateTimePickerInput(),
        }
        # modify labels 
        labels = {
            'title': 'Assignment Name',	
            'startdate': 'Start Date',
            'deadline': 'Deadline',
        }
