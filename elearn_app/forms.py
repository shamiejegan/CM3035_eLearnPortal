from django import forms
from django.forms import ModelForm
from .models import * 
from django.contrib.auth.models import User

class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_student', 'is_instructor', 'photo']