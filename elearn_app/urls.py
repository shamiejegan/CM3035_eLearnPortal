from django.urls import path
from . import views
from . import api
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # root URL
    path("", views.index, name="index"),
    # URLs for user management
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),

    path("profile/<int:pk>", login_required(views.ProfileDetail.as_view()), name="profile"),
    path("updateprofile/<int:pk>", login_required(views.ProfileUpdate.as_view()), name="updateprofile"),

    # URLs for course management
    path("newcourse/", login_required(views.CourseCreate.as_view()), name="newcourse"),
    path("course/<int:pk>", login_required(views.CourseDetail.as_view()), name="course"),
    path("removecourse/<int:pk>", login_required(views.CourseDelete.as_view()), name="removecourse"),
    path("course/<int:pk>/newmaterial", login_required(views.MaterialCreate.as_view()), name="newmaterial"),
    path("deletematerial/<int:course_pk>/<int:pk>", login_required(views.MaterialDelete.as_view()), name="removematerial"),
    path("course/<int:pk>/newassignment", login_required(views.AssignmentCreate.as_view()), name="newassignment"),
    path("deleteassignment/<int:course_pk>/<int:pk>", login_required(views.AssignmentDelete.as_view()), name="removeassignment"),
    path("courselist/", login_required(views.CourseList.as_view()), name="courselist"),

    # URLs for enrollment management
    path("enrollstudents/<int:pk>", login_required(views.EnrollStudents.as_view()), name="enrollstudents"),	#performed by instructor
    path("enroll/<int:pk>", views.enroll, name="enroll"), #performed by student
    path("unenroll/<int:pk>", views.unenroll, name="unenroll"),	
    # URLs for API
    path("api/course/<int:pk>", api.course_detail, name="api_course"),

    # other URLs
    path('404/', views.custom_page_not_found, name='custom_404'), 
]