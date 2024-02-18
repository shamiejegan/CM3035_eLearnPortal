from django.urls import path
from . import views

urlpatterns = [
    # root URL
    path("", views.index, name="index"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    path("course/<int:pk>", views.CourseDetail.as_view(), name="course"),
    path("newcourse/", views.CourseCreate.as_view(), name="newcourse"),
    path("profile/<int:pk>", views.ProfileDetail.as_view(), name="profile"),
    path("updateprofile/", views.ProfileUpdate.as_view(), name="updateprofile"),
]