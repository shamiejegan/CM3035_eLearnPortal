import os
import sys
import django
import csv
from collections import defaultdict

from datetime import datetime
import pytz

sys.path.append('') 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearn_project.settings')
django.setup()

from elearn_app.models import UserProfile, Course, Assignment, Material, Feedback, Notification
from django.contrib.auth.models import Group, User, Permission

def create_groups():
    # create groups if they do not exist
    group_names = ["instructor", "student"]
    instructor_permissions = ["add_course", "change_course", "delete_course", "view_course", "add_assignment", "change_assignment", "delete_assignment", "view_assignment", "add_material", "change_material","delete_material", "view_material", "change_feedback", "delete_feedback", "view_feedback","add_notification", "view_notification","change_notification"]
    student_permissions = ["view_course", "view_assignment", "view_material","add_feedback", "change_feedback", "delete_feedback", "view_feedback","add_notification", "view_notification","change_notification"]
    for group_name in group_names:
        if not Group.objects.filter(name=group_name).exists():
            group = Group.objects.create(name=group_name)
            # set permissions for each group
            if group_name == "instructor":
                instructor_p = Permission.objects.filter(codename__in=instructor_permissions)
                for permission in instructor_p:
                    group.permissions.add(permission)
            if group_name == "student":
                student_p = Permission.objects.filter(codename__in=student_permissions)
                for permission in student_p:
                    group.permissions.add(permission)
            group.save()


def import_user(csv_file_path): 
    users = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            users[row[0]] = row[1:]
            
    for username, data in users.items(): 
        # check if the user already exists
        if User.objects.filter(username=username).exists():
            continue
        # otherwise add the record to the table
        user = User.objects.create(
            username=username,
            first_name=data[0],
            last_name=data[1],
            email=data[2],
            is_active=True if data[3] == 'TRUE' else False,
        )
        user.set_password(data[4])
        user.save()

def import_userProfile(csv_file_path): 
    userprofiles = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            userprofiles[row[0]] = row[1:]
            
    # delete existing records 
    UserProfile.objects.all().delete()  

    for username, data in userprofiles.items(): 
        # find user based on username
        user = User.objects.get(username=username)
        if user:
            # skip record if the user already exists 
            if UserProfile.objects.filter(user=user).exists():
                continue
            # otherwise add the record to the table 
            userprofile = UserProfile.objects.create(
                user=user,
                is_student=True if data[0] == 'TRUE' else False,
                is_instructor=True if data[1] == 'TRUE' else False,
                photo=data[2],
                status=data[3]
            )
            userprofile.save()

            # assign the user a role of instructor in user groups
            if userprofile.is_instructor:
                group_name = "instructor"
                group = Group.objects.get(name=group_name)
                group_id = group.id
                user.groups.add(group_id)
            if userprofile.is_student:
                group_name = "student"
                group = Group.objects.get(name=group_name)
                group_id = group.id
                user.groups.add(group_id)
            user.save()

def import_course(csv_file_path):
    courses = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            courses[row[0]] = row[1:]
            
    # delete existing records 
    Course.objects.all().delete()  

    for module_code, data in courses.items(): 
        instructor_email = data[1]
        # find the instructor's profile based on their email address 
        instructor = UserProfile.objects.get(user__email=instructor_email)

        if instructor:
            # skip record if the module code already exists 
            if Course.objects.filter(module_code=module_code).exists():
                continue
            # otherwise add the record to the table 
            course = Course.objects.create(
                module_code=module_code,
                title=data[0],
                instructor=instructor,
            )
            
            # save the record
            course.save()

def import_studentenrollment(csv_file_path):
    enrollments = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            enrollments[row[0]] = row[1:]
            
    for student_email, data in enrollments.items(): 
        module_code = data[0]
        # find the student's profile based on their email address 
        student = UserProfile.objects.get(user__email=student_email)
        # find course based on module code
        course = Course.objects.get(module_code=module_code)

        if student and course:
            # skip record if the student is already enrolled in the course
            if course.students.filter(user=student.user).exists():
                continue
            # otherwise add the record to the table 
            course.students.add(student)
            course.save()

def import_assignment(csv_file_path):
    assignments = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            assignments[row[0]] = row[1:]
            
    # delete existing records 
    Assignment.objects.all().delete()  

    for title, data in assignments.items(): 

        # find course based on module code
        course = Course.objects.get(module_code=data[0])

        # clean up datetime data
        naive_start = datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%S")
        aware_start = pytz.utc.localize(naive_start)
        native_end = datetime.strptime(data[2], "%Y-%m-%dT%H:%M:%S")
        aware_end = pytz.utc.localize(native_end)

        # load data to record table 
        assignment = Assignment.objects.create(
            title=title,
            course=course,
            startdate=aware_start,
            deadline=aware_end
        )
        # save the record
        assignment.save()

def import_material(csv_file_path):
    materials = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            materials[row[0]] = row[1:]
            
    # delete existing records 
    Material.objects.all().delete()  

    for title, data in materials.items(): 
        # find course based on module code
        course = Course.objects.get(module_code=data[0])

        # load data to record table 
        material = Material.objects.create(
            title=title,
            course=course,
            file=data[1]
        )
        material.save()

def import_feedback(csv_file_path):
    feedbacks = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            feedbacks[row[0]] = row[1:]
            
    # delete existing records 
    Feedback.objects.all().delete()  

    for module_code, data in feedbacks.items(): 
        student_email = data[0]
        # find the student's profile based on their email address 
        student = UserProfile.objects.get(user__email=student_email)
        # find course based on module code
        course = Course.objects.get(module_code=module_code)

        if student and course:
            # otherwise add the record to the table 
            feedback = Feedback.objects.create(
                course=course,
                student=student,
                feedback_text=data[1],
            )
            
            # save the record
            feedback.save()

def import_notification(csv_file_path):
    notifications = defaultdict(list)

    # read data from csv 
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = csv_reader.__next__() 
        for row in csv_reader: 
            notifications[row[0]] = row[1:]
            
    # delete existing records 
    Notification.objects.all().delete()  

    for to_u, data in notifications.items(): 
        # find course based on module code
        course = Course.objects.get(module_code=data[1])
        to_user = UserProfile.objects.get(user__email=to_u)
        from_user = UserProfile.objects.get(user__email=data[0])
        # load data to record table 
        notification = Notification.objects.create(
            to_user=to_user,
            from_user=from_user,
            about_course=course,
            type=data[2],
            read_status=True if data[3] == 'TRUE' else False,
            timestamp=datetime.strptime(data[4], "%Y-%m-%dT%H:%M:%S")
        )
        notification.save()