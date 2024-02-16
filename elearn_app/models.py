from django.db import models
from django.contrib.auth.models import User

#REFERENCES: 
# https://docs.djangoproject.com/en/5.0/ref/models/fields/ 
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # will be using first name, last name, email, and is_active fields from User model
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True) 

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    # do not delete the course if the instructor is deleted. Related name courses_taught allows us to access all the courses a student is enrolled in
    instructor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='courses_taught')
    # related name courses_enrolled allows us to access all the courses a student is enrolled in
    students = models.ManyToManyField(UserProfile, related_name='courses_enrolled')

class Material(models.Model):
    # related name materials allows us to access all the materials under a course 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to='course_materials/')

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    # related name assignments allows us to access all the assignments under a course 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=256)
    deadline = models.DateTimeField()

class Grade(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='grades_received')
    grade = models.IntegerField()
    class Meta:
        # Ensure each student has only one grade for each assignment
        unique_together = ('student', 'assignment')  

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedbacks_received')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='feedbacks_given')
    feedback_text = models.TextField()

