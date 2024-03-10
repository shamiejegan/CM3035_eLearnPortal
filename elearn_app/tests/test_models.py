from django.test import TestCase
from ..forms import *
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from .model_factories import *

class CourseModelTest(TestCase):
    def test_course_instructor_relationship(self):
        instructor_profile = UserProfileFactory(is_instructor=True)
        course = CourseFactory(instructor=instructor_profile)
        self.assertEqual(course.instructor.user.username, instructor_profile.user.username)

    def test_course_students_relationship(self):
        student_profile = UserProfileFactory(is_student=True, is_instructor=False)
        course = CourseFactory()
        course.students.add(student_profile)
        self.assertIn(student_profile, course.students.all())

    def test_material_course_relationship(self):
        course = CourseFactory()
        material = MaterialFactory(course=course)
        self.assertEqual(material.course, course)

class UserProfileModelTest(TestCase):
    def test_user_profile_user_relationship(self):
        user = UserFactory()
        user_profile = UserProfileFactory(user=user)
        self.assertEqual(user_profile.user.username, user.username)

    def test_user_profile_student_instructor_relationship(self):
        student_profile = UserProfileFactory(is_student=True)
        instructor_profile = UserProfileFactory(is_instructor=True)
        self.assertTrue(student_profile.is_student)
        self.assertTrue(instructor_profile.is_instructor)

class MaterialModelTest(TestCase):
    def test_material_course_relationship(self):
        course = CourseFactory()
        material = MaterialFactory(course=course)
        self.assertEqual(material.course, course)

    def test_material_file_upload(self):
        course = CourseFactory()
        file = SimpleUploadedFile("testfile.txt", b"file_content")
        material = MaterialFactory(course=course, file=file)
        self.assertEqual(material.file.read(), b"file_content")

class AssignmentModelTest(TestCase):
    def test_assignment_course_relationship(self):
        course = CourseFactory()
        assignment = AssignmentFactory(course=course)
        self.assertEqual(assignment.course, course)

    def test_assignment_deadline_after_startdate(self):
        assignment = AssignmentFactory()
        self.assertTrue(assignment.deadline > assignment.startdate)

class FeedbackModelTest(TestCase):
    def test_feedback_course_relationship(self):
        course = CourseFactory()
        student = UserProfileFactory(is_student=True)
        feedback = FeedbackFactory(course=course, student=student)
        self.assertEqual(feedback.course, course)

    def test_feedback_student_relationship(self):
        course = CourseFactory()
        student = UserProfileFactory(is_student=True)
        feedback = FeedbackFactory(course=course, student=student)
        self.assertEqual(feedback.student, student)

    
class NotificationModelTest(TestCase):
    def test_notification_to_user_relationship(self):
        to_user = UserProfileFactory()
        notification = NotificationFactory(to_user=to_user)
        self.assertEqual(notification.to_user, to_user)

    def test_notification_from_user_relationship(self):
        from_user = UserProfileFactory()
        notification = NotificationFactory(from_user=from_user)
        self.assertEqual(notification.from_user, from_user)

    def test_notification_about_course_relationship(self):
        course = CourseFactory()
        notification = NotificationFactory(about_course=course)
        self.assertEqual(notification.about_course, course)