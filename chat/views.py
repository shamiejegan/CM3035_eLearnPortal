from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def room(request, room_name):
    # get user's name 
    username = request.user.get_full_name()
    # get user's group
    group = Group.objects.get(user=request.user)
    return render(request, 'chat/room.html', {'room_name': room_name, 'username': username, 'auth_group': group.name})
