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
    path("change-photo/", login_required(views.PictureUpdate.as_view()), name="change_photo"),
    path("update-status/", login_required(views.StatusUpdate.as_view()), name="update_status"),
    path("userlist/", login_required(views.UserList.as_view()), name="userlist"),

    # URLs for course management
    path("courselist/", login_required(views.CourseList.as_view()), name="courselist"),
    path("newcourse/", login_required(views.CourseCreate.as_view()), name="newcourse"),
    path("course/<int:pk>", login_required(views.CourseDetail.as_view()), name="course"),
    path("removecourse/<int:pk>", login_required(views.CourseDelete.as_view()), name="removecourse"),
    path("course/<int:pk>/newmaterial", login_required(views.MaterialCreate.as_view()), name="newmaterial"),
    path("deletematerial/<int:course_pk>/<int:pk>", login_required(views.MaterialDelete.as_view()), name="removematerial"),
    path("course/<int:pk>/newassignment", login_required(views.AssignmentCreate.as_view()), name="newassignment"),
    path("deleteassignment/<int:course_pk>/<int:pk>", login_required(views.AssignmentDelete.as_view()), name="removeassignment"),

    # URLs for enrollment management
    path("enroll/<int:pk>", views.enroll, name="enroll"), #performed by student
    path("unenroll/<int:courseid>/<int:studentid>/", views.unenroll, name="unenroll"),	

    # URLs for feedbacks 
    path("feedback/<int:courseid>/", login_required(views.FeedbackCreate.as_view()), name="feedback"),

    # URLs for API
    path("api/course_list/", api.course_list, name="api_courses"),
    path("api/student_mycourses/", api.student_course, name="api_student_course"),
    path("api/teacher_mycourses/", api.teacher_course, name="api_teacher_course"),

    # path for notification 
    path("mark-as-read/<int:pk>", views.mark_as_read, name="mark_as_read"),
    # other URLs
    path('404/', views.custom_page_not_found, name='custom_404'), 
]