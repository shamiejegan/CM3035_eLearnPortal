from django import forms
from django.forms import ModelForm
from .models import * 
from django.contrib.auth.models import User

class UserForm(ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']


class UserProfileForm(ModelForm):
    user_student = forms.ChoiceField(label='Select Role', choices=[(True, 'Student'), (False, 'Instructor')])

    class Meta:
        model = UserProfile
        fields = ['photo']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # photo is optional
        self.fields['photo'].required = False  

    def clean(self):
        cleaned_data = super().clean()
        user_student = cleaned_data.get('user_student')
        cleaned_data['is_student'] = user_student == 'True'
        cleaned_data['is_instructor'] = user_student == 'False'
        return cleaned_data

class UpdateProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = [ 'status', 'photo']

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        # photo and status are optional
        self.fields['photo'].required = False 
        self.fields['status'].required = False 

class CourseForm(forms.ModelForm):
    instructor = User.username

    class Meta:
        model = Course
        fields = ['module_code', 'title', 'students']
