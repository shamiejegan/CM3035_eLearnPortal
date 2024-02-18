from django.shortcuts import render
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect

from .models import * 
from .forms import *
from django.contrib import messages

# Create your views here.
def index(request):
    # first check if the user is logged in, show login page if they are not already logged in  
    if request.user.is_authenticated:
        return render(request, "elearn/index.html")
    else:
        return HttpResponseRedirect("/login")
    

def register(request):
    registered = False

    if request.method == "POST":
        # New request to register a user
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid(): #TODO: Add validation for forms
            user = user_form.save(commit=False)
            user.username = user.email  # Set username as email
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if "photo" in request.FILES:
                profile.photo = request.FILES["photo"]

            profile.save()
            registered = True
        else:
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

def course(request, course_name):
    # load template course.html
    return render(request, "elearn/course.html")