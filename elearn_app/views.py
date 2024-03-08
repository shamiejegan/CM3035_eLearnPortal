from typing import Any
from django.forms import BaseModelForm
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse


from .models import * 
from .forms import *

from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView


def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)    

# User views 
def register(request):
    registered = False

    if request.method == "POST":
        # New request to register a user
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid(): 
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
                    profile.photo = "elearn_app/user_photos/default_user.png"

                # Add user to student group 
                student_group = Group.objects.get(name='student')
                student_group.user_set.add(user)
                profile.is_student = True
                profile.is_instructor = False

                profile.save()
                registered = True
            except IntegrityError:
                # Show warning if the account already exists 
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

@login_required
def index(request):
    # Retrieve the User details associated with the logged-in user
    user = User.objects.get(username=request.user)
    # Retrieve the UserProfile associated with the logged-in user
    user_profile = UserProfile.objects.get(user=request.user)
    # Get courses taught by the instructor (if any)
    courses_taught = user_profile.courses_taught.order_by('module_code')
    # Get courses enrolled by the student (if any)
    courses_enrolled = user_profile.courses_enrolled.order_by('module_code')
    return render(request, "elearn/index.html", {"user":user, "user_profile": user_profile, "courses_taught": courses_taught, "courses_enrolled": courses_enrolled})

class ProfileDetail(DetailView):
    model = User
    template_name = "elearn/profile.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user with primary key
        user = self.get_object()
        # Get the details associated with the logged-in user
        context["requester_user_profile"] = UserProfile.objects.get(user=self.request.user)
        context["requester_enrolled_courses"] = context["requester_user_profile"].courses_enrolled.all()
        # Get the details associated with the profile we are viewing
        user_profile = get_object_or_404(UserProfile, user=user)
        context["courses_taught"] = user_profile.courses_taught.all()
        context["courses_enrolled"] = user_profile.courses_enrolled.all()
        context["user_profile"] = user_profile            
        return context

class ProfileUpdate(UpdateView):
    model = UserProfile
    template_name = "elearn/profile_form.html"
    form_class = UpdateProfileForm
    success_url = "/"

    def get_object(self, queryset=None):
        return self.request.user.userprofile

# Course views
class CourseDetail(DetailView):
    model = Course
    template_name = "elearn/course.html"
    context_object_name = "course"
    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            return {'authenticated': False}        
        else:
            context = super().get_context_data(**kwargs)
            course = self.object
            context["students"] = Course.objects.get(pk=course.id).students.all()
            context["instructor"] = Course.objects.get(pk=course.id).instructor
            context["user_profile"] = UserProfile.objects.get(user=self.request.user)
            context["user"] = self.request.user
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

class CourseDelete(DeleteView):
    model = Course
    template_name = "elearn/course_confirm_delete.html"
    success_url = "/"

class CourseList(ListView):
    model = Course
    template_name = "elearn/course_list.html"
    context_object_name = "courses"

    # sort data by module_code
    def get_queryset(self):
        # Retrieve the queryset of courses and sort them by module_code
        return Course.objects.all().order_by('module_code')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the details associated with the profile we are viewing
        user_profile = UserProfile.objects.get(user=self.request.user) 
        context["courses_taught"] = user_profile.courses_taught.all()
        context["courses_enrolled"] = user_profile.courses_enrolled.all()
        context["user_profile"] = user_profile
        return context

class MaterialCreate(CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "elearn/material_form.html"

    def get_success_url(self):
        return reverse('course', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['pk'])
        context["course"] = course
        return context

    def form_valid(self, form):
        # Get the course object
        course = Course.objects.get(pk=self.kwargs['pk'])
        # add the uploaded material to the course
        material = form.save(commit=False)
        material.course = course
        material.save()
        return super().form_valid(form)

class MaterialDelete(DeleteView):
    model = Material
    template_name = "elearn/material_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        context["course"] = course
        return context
    
    def get_success_url(self):
        return reverse('course', kwargs={'pk': self.kwargs['course_pk']})

class AssignmentCreate(CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "elearn/assignment_form.html"

    def get_success_url(self):
        return reverse('course', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['pk'])
        context["course"] = course
        return context

    def form_valid(self, form):
        # Get the course object
        course = Course.objects.get(pk=self.kwargs['pk'])
        # add assignment to the course
        assignment = form.save(commit=False)
        assignment.course = course
        assignment.save()
        return super().form_valid(form)

class AssignmentDelete(DeleteView):
    model = Assignment
    template_name = "elearn/assignment_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        context["course"] = course
        return context

    def get_success_url(self):
        return reverse('course', kwargs={'pk': self.kwargs['course_pk']})


# Enrollment views
class EnrollStudents(UpdateView):
    model = Course
    template_name = "elearn/enroll_students.html"
    fields = ['students']
    # redirect back to course page after updating the students
    def get_success_url(self):
        return reverse('course', kwargs={'pk': self.kwargs['pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['pk'])
        # get all users with is_student set in their profile
        context["all_students"] = UserProfile.objects.filter(is_student=True)
        # get all the students enrolled in the course so that we can exclude them from the list of students to be enrolled
        context["enrolled_students"] = Course.objects.get(pk=course.id).students.all()
        context["course"] = course
        return context
    
    # add students to db if form is valid 
    def form_valid(self, form):
        # Get list of selected students from the form submission
        selected_student_ids = self.request.POST.getlist('students')
        # Add each of the selected students to the course
        course = form.instance
        for student_id in selected_student_ids:
            student = UserProfile.objects.get(pk=student_id)
            course.students.add(student)  # Add selected students to the course
        
        return super().form_valid(form)

@login_required
def enroll(request, pk):
    course = Course.objects.get(pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    course.students.add(user_profile)
    return HttpResponseRedirect(reverse('course', kwargs={'pk': pk}))

@login_required
def unenroll(request, pk):    
    course = Course.objects.get(pk=pk)
    user_profile = UserProfile.objects.get(user=request.user)
    course.students.remove(user_profile)
    return HttpResponseRedirect("/")

