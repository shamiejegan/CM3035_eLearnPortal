from django.urls import path
from . import views

urlpatterns = [
    # root URL
    path("", views.index, name="index"),
    # URLs for user management
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/<int:pk>", views.ProfileDetail.as_view(), name="profile"),
    path("updateprofile/<int:pk>", views.ProfileUpdate.as_view(), name="updateprofile"),
    # URLs for course management
    path("newcourse/", views.CourseCreate.as_view(), name="newcourse"),
    path("course/<int:pk>", views.CourseDetail.as_view(), name="course"),
    path("removecourse/<int:pk>", views.CourseDelete.as_view(), name="removecourse"),
    path("course/<int:pk>/newmaterial", views.MaterialCreate.as_view(), name="newmaterial"),
    path("course/<int:pk>/newassignment", views.AssignmentCreate.as_view(), name="newassignment"),
    path("courselist/", views.CourseList.as_view(), name="courselist"),
    # URLs for enrollment management
    path("enrollstudents/<int:pk>", views.EnrollStudents.as_view(), name="enrollstudents"),	#performed by instructor
    path("enroll/<int:pk>", views.enroll, name="enroll"), #performed by student
    path("unenroll/<int:pk>", views.unenroll, name="unenroll"),	
    # other URLs
    path('404/', views.custom_page_not_found, name='custom_404'), 
]