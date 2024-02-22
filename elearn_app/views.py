from typing import Any
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.db import IntegrityError

from .models import * 
from .forms import *

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

# Create your views here.
def index(request):
    # first check if the user is logged in, show login page if they are not already logged in  
    if request.user.is_authenticated:
        # Retrieve the User details associated with the logged-in user
        user = User.objects.get(username=request.user)
        # Retrieve the UserProfile associated with the logged-in user
        user_profile = UserProfile.objects.get(user=request.user)
        # Get courses taught by the instructor (if any)
        courses_taught = user_profile.courses_taught.all()
        # Get courses enrolled by the student (if any)
        courses_enrolled = user_profile.courses_enrolled.all()
        return render(request, "elearn/index.html", {"user":user, "user_profile": user_profile, "courses_taught": courses_taught, "courses_enrolled": courses_enrolled})
    else:
        return HttpResponseRedirect("/login")
    

def register(request):
    registered = False

    if request.method == "POST":
        # New request to register a user
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid(): #TODO: Add validation for forms
            try: 
                user = user_form.save(commit=False)
                user.username = user.email  # Set username as email
                user.set_password(user.password)
                user.save()
                profile = profile_form.save(commit=False)
                profile.user = user

                # upload photo if it exists
                if "photo" in request.FILES:
                    profile.photo = request.FILES["photo"]
                else:
                    profile.photo = "static/images/default.jpg"

                # Add user to the appropriate group
                user_student = request.POST.get('user_student') 
                if user_student == 'True':
                    student_group = Group.objects.get(name='student')
                    student_group.user_set.add(user)
                    profile.is_student = True
                    profile.is_instructor = False
                else:
                    instructor_group = Group.objects.get(name='instructor')
                    instructor_group.user_set.add(user)
                    profile.is_student = False
                    profile.is_instructor = True

                profile.save()
                registered = True
            except IntegrityError:
                # Show warning if the 
                return render(request, "elearn/register.html", {"user_form": user_form, "profile_form": profile_form, "registered": registered, "error": "You already have an account. Please login instead."})

        else:
            return render(request, "elearn/register.html", {"user_form": user_form, "profile_form": profile_form, "registered": registered, "error": "Please fill in all entries in the form to register."})
            print(user_form.errors, profile_form.errors)
    else: 
        user_form = UserForm()
        profile_form = UserProfileForm()
    # load template register.html
    return render(request, "elearn/register.html", {"user_form": user_form, "profile_form": profile_form, "registered": registered})

def login_user(request):
    if request.method == "POST":
        # handling form submission
        email = request.POST["email"]
        password = request.POST["password"]
        try: 
            user = User.objects.get(username=email)
            if user.check_password(password):
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect("/")  # Redirect to index page
                    else:
                        return render(request, "elearn/login.html", {"error": "Your account is disabled, please reach out to your administrator to enable it."})
            else:
                return render(request, "elearn/login.html", {"error": "Invalid email or password"})
        except User.DoesNotExist:
            return render(request, "elearn/login.html", {"error": "Invalid email or password"})
    else: 
        # leading the login page
        return render(request, "elearn/login.html")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/login")

class CourseDetail(DetailView):
    model = Course
    template_name = "elearn/course.html"
    context_object_name = "course"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context["students"] = Course.objects.get(pk=course.id).students.all()
        context["instructor"] = Course.objects.get(pk=course.id).instructor
        context["user_profile"] = UserProfile.objects.get(user=self.request.user)
        context["user"] = course.instructor
        # get all the materials for the course
        context["materials"] = course.materials.all()
        # get all the assignments for the course
        context["assignments"] = course.assignments.all()
        return context
    

class CourseCreate(CreateView):
    model = Course
    template_name = "elearn/course_form.html"
    form_class = CourseForm
    success_url = "/"

    def form_valid(self, form):
        user_profile = self.request.user.userprofile
        form.instance.instructor = user_profile
        return super().form_valid(form)
    
class ProfileDetail(DetailView):
    model = UserProfile
    template_name = "elearn/profile.html"
    context_object_name = "user_profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses_taught"] = self.object.courses_taught.all()
        context["courses_enrolled"] = self.object.courses_enrolled.all()
        context["user_profile"] = self.object
        context["user"] = self.object.user
        return context

class ProfileUpdate(UpdateView):
    model = UserProfile
    template_name = "elearn/profile_form.html"
    form_class = UpdateProfileForm
    success_url = "/"

    def get_object(self, queryset=None):
        return self.request.user.userprofile