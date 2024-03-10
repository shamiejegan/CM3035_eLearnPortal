from django.urls import reverse

from rest_framework.test import APITestCase, APIClient

from .model_factories import * 
from ..serializers import *

# TESTS API ENDPOINT
#######################

class TestAPIsUserSignedIn(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()  
        self.client.force_authenticate(user=self.user)
        self.userprofile = UserProfileFactory(user=self.user)
        self.course = CourseFactory(instructor=self.userprofile)

    def test_signed_in_user_course_list_returns200(self):
        response = self.client.get(reverse('api_courses'))
        self.assertEqual(response.status_code, 200)

    def test_signed_student_courses_returns200(self):
        response = self.client.get(reverse('api_student_course'))
        self.assertEqual(response.status_code, 200)

    def test_signed_teacher_courses_returns200(self):
        response = self.client.get(reverse('api_teacher_course'))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.client.force_authenticate(user=None)
        return super().tearDown()

class TestAPIsUserSignedOut(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()  
        self.client.force_authenticate(user=None)
        self.userprofile = UserProfileFactory(user=self.user)
        self.course = CourseFactory(instructor=self.userprofile)

    def test_signed_out_user_course_list_returns200(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('api_courses'))
        self.assertEqual(response.status_code, 200)

    def test_signed_out_student_courses_returns403(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('api_student_course'))
        self.assertEqual(response.status_code, 403)

    def test_signed_out_teacher_courses403(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('api_teacher_course'))
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        self.client.force_authenticate(user=None)
        return super().tearDown()

class TestCourseListValues(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()  
        self.client.force_authenticate(user=self.user)
        self.userprofile = UserProfileFactory(user=self.user)
        self.course = CourseFactory(instructor=self.userprofile)

    def test_course_list_returns_all_courses(self):
        response = self.client.get(reverse('api_courses'))
        self.assertEqual(response.json(), CourseListSerializer(Course.objects.all(), many=True).data)

    def tearDown(self):
        self.client.force_authenticate(user=None)
        return super().tearDown()

class TestStudentCoursesValuesEnrolled(APITestCase):
    def setUp(self):
        self.client = APIClient()  

        # Create a user and their profile
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)

        # Enroll the user in two courses as a student
        self.course1 = CourseFactory(students=[self.userprofile])
        self.course2 = CourseFactory(students=[self.userprofile])

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

    def test_student_courses_return_multiple_records(self):
        response = self.client.get(reverse('api_student_course')) 
        self.assertTrue(len(response.json()) > 1)

    def test_student_courses_return_course_assigned(self):
        response = self.client.get(reverse('api_student_course'))
        response_data = response.json()
        course_ids = [course['module_code'] for course in response_data] 
        self.assertIn(self.course1.module_code, course_ids)
        self.assertIn(self.course2.module_code, course_ids)
    
    def tearDown(self):
        self.client.force_authenticate(user=None)

class TestStudentCoursesValuesNotEnrolled(APITestCase):
    def setUp(self):
        self.client = APIClient()  

        # Create a user and their profile
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)

        # Do not enroll the user in any courses as a student
        self.course1 = CourseFactory()
        self.course2 = CourseFactory()

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

    def test_student_courses_return_no_records(self):
        response = self.client.get(reverse('api_student_course'))  # Adjust this to your actual URL name
        self.assertTrue(len(response.json()) == 0, "API should return no courses for the student")

    def tearDown(self):
        self.client.force_authenticate(user=None)

class TestTeacherCoursesValues(APITestCase):
    def setUp(self):
        self.client = APIClient()  
        
        # Create a user and their profile
        self.user = UserFactory()
        self.userprofile = UserProfileFactory(user=self.user)

        # Create a course for the user as an instructor
        self.course = CourseFactory(instructor=self.userprofile)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

    def test_teacher_courses_return_course_assigned(self):
        response = self.client.get(reverse('api_teacher_course'))
        response_data = response.json()
        course_ids = [course['module_code'] for course in response_data] 
        self.assertIn(self.course.module_code, course_ids)

    def tearDown(self):
        self.client.force_authenticate(user=None)