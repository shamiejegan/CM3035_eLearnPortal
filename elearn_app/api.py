from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser 

from .models import *
from .serializers import *

@csrf_exempt
def course_detail(request, pk): 
    try: 
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist: 
        return HttpResponse(status=400)
    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return JsonResponse(serializer.data)