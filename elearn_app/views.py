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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

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
    # Get notifications for the user
    notifications = user_profile.notifications_recieved.order_by('-timestamp')
    return render(request, "elearn/index.html", {"user":user, "user_profile": user_profile, "courses_taught": courses_taught, "courses_enrolled": courses_enrolled,"notifications": notifications})

class ProfileDetail(DetailView):
    model = User
    template_name = "elearn/profile.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user with primary key
        user = self.get_object()
        # Get the details associated with the logged-in user
        context["user_profile"] = UserProfile.objects.get(user=self.request.user)
        context["enrolled_courses"] = context["user_profile"].courses_enrolled.all()
        # Get the details associated with the profile we are viewing
        user_profile = get_object_or_404(UserProfile, user=user)
        context["other_courses_taught"] = user_profile.courses_taught.all()
        context["other_courses_enrolled"] = user_profile.courses_enrolled.all()
        context["other_user_profile"] = user_profile            
        return context

class PictureUpdate(UpdateView):
    model = UserProfile
    template_name = "elearn/change_photo.html"
    form_class = UserProfileForm
    success_url = "/"

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        # Get the user profile object
        user_profile = form.save(commit=False)
        # add the uploaded photo to the user profile
        user_profile.photo = form.cleaned_data['photo']
        user_profile.save()
        return super().form_valid(form)
    
class StatusUpdate(UpdateView):
    model = UserProfile
    template_name = "elearn/change_status.html"
    form_class = UpdateStatusForm
    success_url = "/"

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        # Get the user profile object
        user_profile = form.save(commit=False)
        # add the uploaded photo to the user profile
        user_profile.status = form.cleaned_data['status']
        user_profile.save()
        return super().form_valid(form)
    
class UserList(ListView):
    model = User
    template_name = "elearn/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        # Retrieve the search query 
        search_query = self.request.GET.get('search')
        # Filter users by first name, last name, and email starting with the value entered in the search query
        if search_query:
            queryset = User.objects.filter(first_name__startswith=search_query) | User.objects.filter(last_name__startswith=search_query) | User.objects.filter(email__startswith=search_query)
        else:
            # If there is no search query, return all users
            queryset = User.objects.all()
        # Order the results by first name (A-Z)
        return queryset.order_by('first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the details associated with the profile we are viewing
        user_profile = UserProfile.objects.get(user=self.request.user)
        context["user_profile"] = user_profile
        return context

# Course views
class CourseDetail(DetailView):
    permission_required = 'elearn_app.view_course'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.view_course'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

    model = Course
    template_name = "elearn/course.html"
    context_object_name = "course"
    def get_context_data(self, **kwargs):
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
        # get all the feedback for the course 
        context["feedbacks"] = course.feedbacks_received.all()
        context["feedbacks_shared"] = context["user_profile"].feedbacks_given.all()
        # for chat
        context["username"] = self.request.user.get_full_name()
        context["auth_group"] = "student" if context["user_profile"].is_student else "instructor" if context["user_profile"].is_instructor else "admin"
        context["room_name"] = course.module_code
        return context

class CourseCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'elearn_app.add_course'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.add_course'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

    # if there is no issues with permissions
    model = Course
    template_name = "elearn/course_form.html"
    form_class = CourseForm
    success_url = "/"

    def form_valid(self, form):
        user_profile = self.request.user.userprofile
        form.instance.instructor = user_profile
        return super().form_valid(form)

class CourseDelete(DeleteView):
    permission_required = 'elearn_app.delete_course'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.delete_course'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

    # if there is no issues with permissions
    model = Course
    template_name = "elearn/course_confirm_delete.html"
    success_url = "/"

class CourseList(ListView):
    permission_required = 'elearn_app.view_course'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.view_course'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

    model = Course
    template_name = "elearn/course_list.html"
    context_object_name = "courses"

    # sort data by module_code
    def get_queryset(self):
        search_query = self.request.GET.get('search')
        # Filter users by first name, last name, and email starting with the value entered in the search query
        if search_query:
            queryset = Course.objects.filter(module_code__startswith=search_query) | Course.objects.filter(title__contains=search_query) 
        else:
            # If there is no search query, return all users
            queryset = Course.objects.all()
        # Order the results by first name (A-Z)
        return queryset.order_by('module_code')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the details associated with the profile we are viewing
        user_profile = UserProfile.objects.get(user=self.request.user) 
        context["courses_taught"] = user_profile.courses_taught.all()
        context["courses_enrolled"] = user_profile.courses_enrolled.all()
        context["user_profile"] = user_profile
        return context

class MaterialCreate(CreateView):
    permission_required = 'elearn_app.add_material'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.add_material'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

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

        # Create a notification for each student in the course
        for student in course.students.all():
            notification = Notification(to_user=student, from_user=course.instructor, about_course=course, type="New Material Added")
            notification.save()

        return super().form_valid(form)

class MaterialDelete(DeleteView):
    permission_required = 'elearn_app.delete_material'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.delete_material'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

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
    permission_required = 'elearn_app.add_assignment'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.add_assignment'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

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

        # Create a notification for each student in the course
        for student in course.students.all():
            notification = Notification(to_user=student, from_user=course.instructor, about_course=course, type="New Assignment Added")
            notification.save()

        return super().form_valid(form)

class AssignmentDelete(DeleteView):
    permission_required = 'elearn_app.delete_assignment'

    def dispatch(self, request, *args, **kwargs):
        try:
            if not request.user.has_perm('elearn_app.delete_assignment'):
                # Return 404 error if user does not have permission to add a course
                return HttpResponse(status=404) 
        except PermissionDenied:
            # Handle PermissionDenied exception without raising it further
            pass
        return super().dispatch(request, *args, **kwargs)

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

    # Create a notification to instructor when student enrolls in the course
    message = user_profile.user.get_full_name() + " has enrolled in the course."
    notification = Notification(to_user=course.instructor, from_user=user_profile, about_course=course, type=message)
    notification.save()

    return HttpResponseRedirect(reverse('course', kwargs={'pk': pk}))

@login_required
def unenroll(request, courseid, studentid):    
    course = Course.objects.get(pk=courseid)
    user_profile = UserProfile.objects.get(user=studentid)
    course.students.remove(user_profile)
    return HttpResponseRedirect("/")


# Feedback views
class FeedbackCreate(CreateView): 
    model = Feedback
    form_class = FeedbackForm
    template_name = "elearn/feedback_form.html"

    def get_success_url(self):
        return reverse('course', kwargs={'pk': self.kwargs['courseid']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['courseid'])
        student = UserProfile.objects.get(user=self.request.user)
        context["course"] = course
        context["student"] = student
        return context

    def form_valid(self, form):
        # Get the course object
        course = Course.objects.get(pk=self.kwargs['courseid'])
        student = UserProfile.objects.get(user=self.request.user)
        # add feedback to the course
        feedback = form.save(commit=False)
        feedback.course = course
        feedback.student = student
        feedback.save()
        return super().form_valid(form)
    
# notifications 
@login_required
def mark_as_read(request, pk):
    # try to get the notificatino based on pk
    notification = Notification.objects.get(pk=pk)
    # confirm that the notification comes from the user
    if notification.to_user != request.user.userprofile:
        return HttpResponse(status=404)
    # mark the notification as read
    notification.read_status = True
    notification.save()

    return HttpResponseRedirect("/")