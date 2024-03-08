from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser 
from rest_framework.decorators import api_view

from .models import *
from .serializers import *

@api_view(['GET'])
def course_detail(request, pk): 
    try: 
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist: 
        return HttpResponse(status=400)
    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return JsonResponse(serializer.data)