import factory
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import *

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    # user is a instructor by default
    user = factory.SubFactory(UserFactory)
    is_student = False
    is_instructor = True

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    module_code = factory.Sequence(lambda n: f'CS{1000 + n}')
    title = factory.Faker('sentence', nb_words=5)
    instructor = factory.SubFactory(UserProfileFactory)

    @factory.post_generation
    def students(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of students were passed in, use them
            for student in extracted:
                self.students.add(student)



class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    title = factory.Faker('sentence', nb_words=3)
    course = factory.SubFactory(CourseFactory)
    file = factory.django.FileField(filename='test_files/test.pdf')

class AssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assignment

    title = factory.Faker('sentence', nb_words=3)
    course = factory.SubFactory(CourseFactory)
    startdate = timezone.now()
    deadline = factory.LazyAttribute(lambda o: o.startdate + timezone.timedelta(days=7))

class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback

    course = factory.SubFactory(CourseFactory)
    student = factory.SubFactory(UserProfileFactory)
    feedback_text = factory.Faker('paragraph')

class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    to_user = factory.SubFactory(UserProfileFactory)
    from_user = factory.SubFactory(UserProfileFactory)
    about_course = factory.SubFactory(CourseFactory)
    type = factory.Faker('word')
    read_status = False
