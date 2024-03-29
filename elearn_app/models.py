from django.db import models
from django.contrib.auth.models import User

#REFERENCES: 
# https://docs.djangoproject.com/en/5.0/ref/models/fields/ 
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model

class UserProfile(models.Model): # will be using first name, last name, email, and is_active fields from User model
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='elearn_app/user_photos/', blank=True, null=True) 
    status = models.CharField(max_length=256, blank=True, null=True, default="")

    def __str__(self):
        return self.user.username

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    module_code = models.CharField(max_length=256, unique=True)
    title = models.CharField(max_length=256)
    # do not delete the course if the instructor is deleted. Related name courses_taught allows us to access all the courses a student is enrolled in
    instructor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='courses_taught')
    # related name courses_enrolled allows us to access all the courses a student is enrolled in, null=True allows for courses with no students
    students = models.ManyToManyField(UserProfile, related_name='courses_enrolled', blank=True)

    def __str__(self):
        return self.module_code # string returned as module code due to its uniqueness

class Material(models.Model):
    # related name materials allows us to access all the materials under a course 
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256, blank=False, null=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials', blank=False, null=False)
    file = models.FileField(upload_to='course_materials/', blank=False, null=False)

    def __str__(self):
        return self.title

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    # related name assignments allows us to access all the assignments under a course 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    startdate = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedbacks_received')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='feedbacks_given')
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feedback_text

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications_recieved')
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications_sent')
    about_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=256)
    read_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type