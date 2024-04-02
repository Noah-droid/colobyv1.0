from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import Room, UploadedFile, Message, Task
from serializers.serializers import TaskSerializer 
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.conf import settings
from datetime import timezone, datetime
import tempfile
import shutil


User = get_user_model()
# @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="media"))
# class MessageAPITests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpassword'
#         )
#         self.token, created = Token.objects.get_or_create(user=self.user)
#         self.room = Room.objects.create(
#             name='Test Room',
#             slug='test-room',
#             is_private=False
#         )

#     def authenticate_client(self):
#         self.client = APIClient()
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
#         self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
#         print(self.token.key)


#     # def test_send_message(self):
#     #     self.authenticate_client()
#     #     url = reverse('send-message', kwargs={'room_slug': 'test-room'})
#     #     data = {
#     #         'message_text': 'Hello world!',
#     #     }
#     #     response = self.client.post(url, data)
#     #     print(response.status_code)
#     #     print(response.content)
#     #     self.assertEqual(response.status_code, 201)
#     #     self.assertTrue(Message.objects.filter(message_text="Hello world!").exists())

#     # def test_send_with_media(self):
#     #     self.authenticate_client()
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
#     #     url = reverse('send-message', kwargs={'room_slug': 'test-room'})
#     #     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#     #         temp_file.write(b'This is the content of the test file.')

#     #     with open(temp_file.name, 'rb') as media_file:
#     #         data = {
#     #             'alt_text': 'Test this pic!',
#     #             'media_file': media_file
#     #         }
#     #         response = self.client.post(url, data, format='multipart')
#     #         print(response.status_code)
#     #         print(response.content)
#     #         self.assertEqual(response.status_code, 201)

#     # def test_get_messages(self):
#     #     self.authenticate_client()
#     #     url = reverse('get-message', kwargs={'room_slug': 'test-room'})
#     #     response = self.client.get(url)
#     #     print(response.status_code)
#     #     print(response.content)
#     #     self.assertEqual(response.status_code, 200)

#     def test_unauthenticated_user_cannot_send_message(self):
#         url = reverse('send-message', kwargs={'room_slug': 'test-room'})
#         data = {
#             'message_text': 'Hello world!',
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 401)


# @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="media"))
# class RoomAPITests(TestCase):
#     """Tests for Room API."""
#     def setUp(self):
#         """Creates a test user and room."""
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@example.com',
#             password='testpassword'
#         )
#         self.room = Room.objects.create(
#             name='Test Room',
#             slug='test-room',
#             is_private=False
#         )

#     def test_create_private_room(self):
#         """Tests that a logged-in user can create a private room."""
#         self.client.login(username='testuser', password='testpassword')
#         url = reverse('room-create')
#         data = {
#             'room_name': 'Private Room',
#             'is_private': 'on',
#         }
#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(Room.objects.filter(name='Private Room', is_private=True).exists())

#     def test_create_public_room(self):
#         """Tests that a logged-in user can create a public room."""
#         self.client.login(username='testuser', password='testpassword')
#         url = reverse('room-create')
#         data = {
#             'room_name': 'Public Room',
#             'is_private': '',
#         }
#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(Room.objects.filter(name='Public Room', is_private=False).exists())

#     def test_join_private_room(self):
#         """Tests that a logged-in user cannot join a private room without being invited."""
#         self.client.login(username='testuser', password='testpassword')
#         private_room = Room.objects.create(
#             name='Private Room',
#             slug='private-room',
#             is_private=True
#         )
#         url = reverse('room-join')
#         data = {
#             'room_name': 'private-room',
#             'room_type': 'private',
#         }
#         response = self.client.post(url, data, follow=True)

#         self.assertEqual(response.status_code, 403)

#     def test_join_public_room(self):
#         """Tests that a logged in user can a public room."""
#         self.client.login(username='testuser', password='testpassword')
#         public_room = Room.objects.create(
#             name='Public Room',
#             slug='public-room',
#             is_private=False
#         )
#         url = reverse('public-room', kwargs={'slug': 'public-room'})
#         data = {
#             'room_name': 'public-room',
#             'room_type': 'public',
#         }

#         response = self.client.post(url, data, follow=True)

#         self.assertEqual(response.status_code, 200)

#     def test_generate_unique_link(self):
#         """Tests that a unique link is generated when creating a room."""
#         self.client.login(username='testuser', password='testpassword')
#         url = reverse('room-create')
#         data = {
#             'room_name': 'Unique-Link-Room',
#             'is_private': '',
#         }
#         response = self.client.post(url, data)

#         self.assertEqual(response.status_code, 302)

#         created_room = Room.objects.get(name='Unique-Link-Room')

#         self.assertTrue(created_room.unique_link)


# @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="media"))
# class TaskAPITests(TestCase):
#     """Tests for Task API."""
#     def setUp(self):
#         """Setup test user, room, tasks, and authenticated client."""
#         self.user = User.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')

#         self.room = Room.objects.create(name='Test Room', slug='test-room')

#         current_time = datetime.now(timezone.utc)

#         self.task1 = Task.objects.create(title='Task 1', room=self.room, due_date=datetime(
#         current_time.year,
#         current_time.month,
#         current_time.day,
#         current_time.hour,
#         current_time.minute,
#         current_time.second,
#         current_time.microsecond,
#         ).astimezone(timezone.utc), assigned_to=self.user,)
#         self.task2 = Task.objects.create(title='Task 2', room=self.room, due_date=datetime(
#         current_time.year,
#         current_time.month,
#         current_time.day,
#         current_time.hour,
#         current_time.minute,
#         current_time.second,
#         current_time.microsecond,
#         ).astimezone(timezone.utc), assigned_to=self.user,)

#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)
    
#     def test_task_list_create_view(self):
#         """
#         Tests that calling the API endpoint for creating new tasks:

#         - Sends a POST request to the correct URL with appropriate data.
#         - Returns a created status code (201).
#         - Creates and saves the new task in the database.
#         """
#         url = reverse('task-list', kwargs={'slug': self.room.slug})

#         data = {'title': 'New Task',
#                 'description': 'Task description',  
#                 'due_date': '2023-12-21T12:00:00Z', 
#                 'room': self.room.id,  
#                 'assigned_to': self.user.id, }

#         response = self.client.post(url, data, format='json')
#         print(response.content)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         self.assertEqual(Task.objects.count(), 3)

#     # def test_task_detail(self):
#     #     """
#     #     Tests that the API endpoint for managing individual tasks:

#     #     - Retrieves the existing task information with a GET request.
#     #     - Updates the task title with a PUT request (200 status code).
#     #     - Verifies the updated title in the database.
#     #     - Deletes the task with a DELETE request (204 status code).
#     #     - Confirms only one task remains in the database.
#     #     """
#     #     url = reverse('task-detail', kwargs={'pk': self.task1.pk})

#     #     response = self.client.get(url)
#     #     print(response.content)
#     #     self.assertEqual(response.status_code, status.HTTP_200_OK)

#     #     updated_data = {'title': 'Updated Task',
#     #                     'description': 'Task description',  
#     #                     'due_date': '2023-12-21T12:00:00Z', 
#     #                     'room': self.room.id,  
#     #                     'assigned_to': self.user.id,}
#     #     response = self.client.put(url, updated_data, format='json')
#     #     print(response.content)
#     #     self.assertEqual(response.status_code, status.HTTP_200_OK)

#     #     self.task1.refresh_from_db()
#     #     self.assertEqual(self.task1.title, 'Updated Task')

#     #     print("Task count before deletion:", Task.objects.count())
#     #     response = self.client.delete(url)
#     #     print("Task count after deletion:", Task.objects.count())
#     #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#     #     self.assertEqual(Task.objects.count(), 1)


from django.test import TestCase
from rest_framework.test import APIClient
from cowork.models import Room
from cowork.models import UploadedFile, Branch, Commit, UploadedFileVersion
from serializers.serializers import UploadedFileSerializer

@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="media"))
class UploadFileViewTests(TestCase):

    def setUp(self):
        # Create a room
        self.room = Room.objects.create(name='Test Room')

        # Create a user
        self.user = User.objects.create(username='testuser')

        # Create an uploaded file
        self.file = SimpleUploadedFile('testfile.txt', b'This is a test file.')

    def test_create_file(self):
        # Create an API client
        client = APIClient()
        client.force_authenticate(user=self.user)

        # Send a POST request to the upload file view with the file
        data = {
            'file': self.file,
            'room_slug': self.room.slug,
        }
        response = client.post('/api/v1/room/upload/file/<str:room_slug>/', data=data, format='multipart')

        # Verify that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify that the uploaded file was saved to the database
        uploaded_file = UploadedFile.objects.get(pk=response.data['id'])
        self.assertEqual(uploaded_file.file, self.file)

        # Verify that the commit was created
        commit = Commit.objects.get(pk=uploaded_file.commit.pk)
        self.assertEqual(commit.uploader, self.user)

        # Verify that the version was created
        version = UploadedFileVersion.objects.get(pk=uploaded_file.version.pk)
        self.assertEqual(version.file, self.file)

        # Verify that the branch was created
        branch = Branch.objects.get(pk=uploaded_file.branch.pk)
        self.assertEqual(branch.original_file, uploaded_file)
        self.assertEqual(branch.created_by, self.user)
        self.assertEqual(branch.room, self.room)
