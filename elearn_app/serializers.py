from rest_framework import serializers
from .models import *

class CourseSerializer(serializers.ModelSerializer):
    # get the instructor's name based on their id (only 1 instructor per course)
    instructor_name = serializers.CharField(source='instructor.user.get_full_name', read_only=True)

    # get the student's name based on their id (multiple students per course)
    students = serializers.SerializerMethodField(read_only=True)
    def get_students(self, obj):
        return [student.user.get_full_name() for student in obj.students.all()]

    class Meta:
        model = Course
        fields = ['id', 'module_code', 'title', 'instructor_name', 'students']
