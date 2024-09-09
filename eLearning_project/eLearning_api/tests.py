# I wrote this code

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import UserProfile, UserStatus, Course, CourseMaterial
from .serializers import UserSerializer, UserProfileSerializer
from .utils import Status, UserContactStatus, CourseMaterialType
from datetime import date

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.course = Course.objects.create(created_by=self.user, title='Test Course', category='Test')

    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(
            created_by=self.user,
            dob=date(1990, 1, 1),
            occupation='Student',
            location='Johannesburg'
        )
        self.assertTrue(isinstance(profile, UserProfile))
        self.assertEqual(profile.created_by, self.user)

    def test_course_creation(self):
        self.assertTrue(isinstance(self.course, Course))
        self.assertEqual(self.course.title, 'Test Course')

    def test_course_material_creation(self):
        material = CourseMaterial.objects.create(
            course=self.course,
            created_by=self.user,
            type=CourseMaterialType.Pdf,
            title='Test Material'
        )
        self.assertTrue(isinstance(material, CourseMaterial))
        self.assertEqual(material.course, self.course)

class SerializerTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_serializer(self):
        serializer = UserSerializer(instance=self.user)
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')

    def test_user_profile_serializer(self):
        profile = UserProfile.objects.create(
            created_by=self.user,
            dob=date(1990, 1, 1),
            occupation='Student',
            location='Johannesburg'
        )
        serializer = UserProfileSerializer(instance=profile)
        self.assertEqual(serializer.data['occupation'], 'Student')
        self.assertEqual(serializer.data['location'], 'Johannesburg')

class ViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

    def test_user_list_view(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course(self):
        url = reverse('course-list')
        data = {
            'title': 'Test Course',
            'description': 'This is a test course',
            'category': 'Test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.get().title, 'Test Course')

    def test_create_user_status(self):
        url = reverse('userstatus-list')
        data = {
            'message': 'Test status update',
            'created_by_id': self.user.id,
            'created_by_username': self.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserStatus.objects.count(), 1)
        self.assertEqual(UserStatus.objects.get().message, 'Test status update')

class UtilsTestCase(TestCase):
    def test_status_enum(self):
        self.assertEqual(Status.Active.value, 10)
        self.assertEqual(Status.Blocked.value, 40)
        self.assertEqual(Status.Archived.value, 50)

    def test_user_contact_status_enum(self):
        self.assertEqual(UserContactStatus.Active.value, 10)
        self.assertEqual(UserContactStatus.Invited.value, 20)
        self.assertEqual(UserContactStatus.Archived.value, 50)

    def test_course_material_type_enum(self):
        self.assertEqual(CourseMaterialType.Generic.value, 0)
        self.assertEqual(CourseMaterialType.Pdf.value, 20)
        self.assertEqual(CourseMaterialType.Excel.value, 40)

# end of code I wrote