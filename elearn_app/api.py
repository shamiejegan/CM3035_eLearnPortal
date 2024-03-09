from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import *
from .serializers import *

# only this API is accessible to members of the public. 
@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request): 
    if request.method == 'GET':
        courses = Course.objects.all()
        serializer = CourseListSerializer(courses, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def student_course(request):
    user_profile = request.user.userprofile
    course_ids = Course.objects.filter(students=user_profile).values_list('id', flat=True)
    courses = Course.objects.filter(id__in=course_ids)
    serializer = StudentCourseSerializer(courses, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def teacher_course(request):
    user_profile = request.user.userprofile
    courses = Course.objects.filter(instructor=user_profile)
    serializer = TeacherCourseSerializer(courses, many=True)
    return JsonResponse(serializer.data, safe=False)