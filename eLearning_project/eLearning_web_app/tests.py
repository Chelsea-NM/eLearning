from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from eLearning_api.models import UserProfile, Course, CourseMaterial, UserCourse, UserStatus
from eLearning_api.utils import Status
from .forms import NameForm, UserProfileForm, NewCourseForm, NewCourseMaterialForm
from datetime import datetime, timedelta
from channels.testing import WebsocketCommunicator
from eLearning_web_app.consumers import ChatConsumer
from asgiref.sync import sync_to_async
import json

class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)

    def test_home_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_search_courses_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('search_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_courses.html')

    def test_add_course_view(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.get(reverse('add_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_add_update.html')

    def test_view_course(self):
        self.client.login(username='testuser', password='12345')
        course = Course.objects.create(title='Test Course', created_by=self.teacher, category='Test')
        response = self.client.get(reverse('course', args=[course.course_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_view.html')

class FormTestCase(TestCase):
    def test_name_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmpassword': 'password123'
        }
        form = NameForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_name_form_passwords_mismatch(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmpassword': 'password456'
        }
        form = NameForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirmpassword', form.errors)

    def test_user_profile_form_valid(self):
        form_data = {
            'dob': '1990-01-01',
            'occupation': 'Student',
            'location': 'Test City'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_new_course_form_valid(self):
        form_data = {
            'title': 'Test Course',
            'description': 'This is a test course',
            'category': 'Test',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M')
        }
        form = NewCourseForm(data=form_data)
        self.assertTrue(form.is_valid())

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)

    def test_user_profile_creation(self):
        user_profile = UserProfile.objects.get(created_by=self.user)
        self.assertIsNotNone(user_profile)

    def test_course_creation(self):
        course = Course.objects.create(title='Test Course', created_by=self.teacher, category='Test')
        self.assertIsNotNone(course)
        self.assertEqual(course.title, 'Test Course')

    def test_user_course_enrollment(self):
        course = Course.objects.create(title='Test Course', created_by=self.teacher, category='Test')
        user_course = UserCourse.objects.create(user=self.user, course=course, created_by=self.user)
        self.assertIsNotNone(user_course)
        self.assertEqual(user_course.user, self.user)
        self.assertEqual(user_course.course, course)

class UtilityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)

    def test_user_type(self):
        self.assertFalse(self.user.groups.filter(name='Teacher').exists())
        self.assertTrue(self.teacher.groups.filter(name='Teacher').exists())

    def test_course_status(self):
        course = Course.objects.create(title='Test Course', created_by=self.teacher, category='Test')
        self.assertEqual(course.status, Status.Active)

    def test_user_status_creation(self):
        status_update = UserStatus.objects.create(created_by=self.user, message='Test status')
        self.assertIsNotNone(status_update)
        self.assertEqual(status_update.message, 'Test status')

class ComprehensiveViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)
        self.course = Course.objects.create(title='Test Course', created_by=self.teacher, category='Test')

    def test_update_course(self):
        self.client.login(username='teacher', password='12345')
        update_url = reverse('updatecourse', args=[self.course.course_id])
        response = self.client.post(update_url, {
            'title': 'Updated Course',
            'description': 'Updated description',
            'category': 'Updated Category',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        updated_course = Course.objects.get(pk=self.course.course_id)
        self.assertEqual(updated_course.title, 'Updated Course')

    def test_add_course_material(self):
        self.client.login(username='teacher', password='12345')
        add_material_url = reverse('add_course_material', args=[self.course.course_id])
        response = self.client.post(add_material_url, {
            'title': 'Test Material',
            'description': 'Test description',
            'file_name': SimpleUploadedFile("test.txt", b"file_content"),
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful addition
        self.assertTrue(CourseMaterial.objects.filter(course=self.course).exists())

    def test_delete_course_material(self):
        material = CourseMaterial.objects.create(
            course=self.course, 
            created_by=self.teacher, 
            title='Test Material',
            file_name=SimpleUploadedFile("test.txt", b"file_content")
        )
        self.client.login(username='teacher', password='12345')
        delete_url = reverse('delete_course_material', args=[material.course_material_id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(CourseMaterial.objects.filter(pk=material.course_material_id).exists())

class PermissionAndAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)
        self.course = Course.objects.create(title='Test Course', created_by=self.teacher, category='Test')

    def test_add_course_permission(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_courses'))
        self.assertEqual(response.status_code, 403)  # Forbidden for non-teachers

    def test_update_course_permission(self):
        self.client.login(username='testuser', password='12345')
        update_url = reverse('updatecourse', args=[self.course.course_id])
        response = self.client.post(update_url, {'title': 'Updated Course'})
        self.assertEqual(response.status_code, 403)  # Forbidden for non-course creators

    def test_view_course_authentication(self):
        view_url = reverse('course', args=[self.course.course_id])
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login for unauthenticated users

class CustomMethodTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)

    def test_user_list_view_method(self):
        self.client.login(username='teacher', password='12345')
        response = self.client.get(reverse('users_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)
        self.assertTrue(len(response.context['users']) > 0)

    def test_course_list_view_method(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.context)

class ExtensiveFormValidationTestCase(TestCase):
    def test_name_form_username_taken(self):
        User.objects.create_user(username='existinguser', password='12345')
        form_data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirmpassword': 'password123'
        }
        form = NameForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_new_course_form_past_due_date(self):
        form_data = {
            'title': 'Test Course',
            'description': 'This is a test course',
            'category': 'Test',
            'due_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        }
        form = NewCourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

    def test_new_course_material_form_file_type(self):
        form_data = {
            'title': 'Test Material',
            'description': 'This is a test material',
            'file_name': SimpleUploadedFile("test.exe", b"file_content"),
        }
        form = NewCourseMaterialForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('file_name', form.errors)

class IntegrationTestCase(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345')
        self.teacher_group = Group.objects.create(name='Teacher')
        self.teacher.groups.add(self.teacher_group)
        UserProfile.objects.create(created_by=self.user)
        UserProfile.objects.create(created_by=self.teacher)

    def test_course_creation_and_enrollment_workflow(self):
        # Teacher creates a course
        self.client.login(username='teacher', password='12345')
        course_data = {
            'title': 'Integration Test Course',
            'description': 'This is a test course',
            'category': 'Test',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M')
        }
        response = self.client.post(reverse('add_courses'), course_data)
        self.assertEqual(response.status_code, 302)
        course = Course.objects.get(title='Integration Test Course')

        # Student enrolls in the course
        self.client.login(username='testuser', password='12345')
        enroll_url = reverse('enroll_course', args=[course.course_id])
        response = self.client.post(enroll_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserCourse.objects.filter(user=self.user, course=course).exists())

        # Student views the course
        view_url = reverse('course', args=[course.course_id])
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Course')

class ChatFunctionalityTestCase(TransactionTestCase):
    async def test_chat_consumer(self):
        user = await sync_to_async(User.objects.create_user)(username='testuser', password='12345')
        course = await sync_to_async(Course.objects.create)(title='Test Course', created_by=user, category='Test')

        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{course.course_id}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Test sending message
        await communicator.send_json_to({"message": "Hello, chat!"})
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"message": "Hello, chat!"})

        # Close
        await communicator.disconnect()

    async def test_chat_room_view(self):
        user = await sync_to_async(User.objects.create_user)(username='testuser', password='12345')
        course = await sync_to_async(Course.objects.create)(title='Test Course', created_by=user, category='Test')

        client = Client()
        await sync_to_async(client.login)(username='testuser', password='12345')

        url = reverse('chat_room', args=[course.course_id])
        response = await sync_to_async(client.get)(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_room.html')

# end of code I wrote