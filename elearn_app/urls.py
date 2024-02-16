from django.urls import path

from . import views

urlpatterns = [
    # root URL
    path("", views.index, name="index"),
]