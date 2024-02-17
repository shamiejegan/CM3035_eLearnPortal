from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    # load template index.html
    return render(request, "elearn/index.html")

def login(request):
    # load template login.html
    return render(request, "elearn/login.html")