from django.contrib import admin
from .models import *

# Register all models  
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    pass

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    pass

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass
