from django.urls import path
from . import views

urlpatterns = [
    # root URL
    path("", views.index, name="index"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    path("newcourse/", views.CourseCreate.as_view(), name="newcourse"),
    path("course/<int:pk>", views.CourseDetail.as_view(), name="course"),
    path("removecourse/<int:pk>", views.CourseDelete.as_view(), name="removecourse"),
    path("course/<int:pk>/newmaterial", views.MaterialCreate.as_view(), name="newmaterial"),
    path("course/<int:pk>/newassignment", views.AssignmentCreate.as_view(), name="newassignment"),
    path("profile/<int:pk>", views.ProfileDetail.as_view(), name="profile"),
    path("updateprofile/<int:pk>", views.ProfileUpdate.as_view(), name="updateprofile"),
    path("enrollstudents/<int:pk>", views.EnrollStudents.as_view(), name="enrollstudents"),	
    path("unenroll/<int:pk>", views.unenroll, name="unenroll"),	
    path('404/', views.custom_page_not_found, name='custom_404'), 
]