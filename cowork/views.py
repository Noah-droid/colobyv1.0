import string
import random
import mimetypes
# from serializers.serializers import UploadedFileSerializer, BranchSerializer, UploadedFileVersionSerializer, CommitSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.http import HttpResponse, Http404, FileResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib import messages
from rest_framework import status, generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import ValidationError
from serializers.serializers import (
    TaskSerializer, CommentSerializer,
    SendMessageSerializer, ReceiveMessageSerializer,
    RoomSerializer,
    # BranchSerializer,
    UserNoteSerializer,
    FeatureRequestSerializer,
    NotificationSerializer,
    UserSerializer,
    FileSerializer,
    StagedFileSerializer
    # Commit, UploadedFileVersion

)

import hashlib
from .models import (Task, Comment, Room, Message,
                    File, StagedFile, 
                    Branch,
                     UserNote, FeatureRequest, Notification
                     )
import logging

logger = logging.getLogger(__name__)


from .models import APIKey
from .authentication import APIKeyAuthentication

class ProtectedAPIView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Protected API endpoint"}, status=status.HTTP_200_OK)

class GenerateAPIKeyView(APIView):
    def post(self, request):
        # Get the user making the request
        user = request.user

        # Create a new API key for the user
        api_key = APIKey.create_for_user(user)

        return Response({"api_key": api_key.key}, status=status.HTTP_201_CREATED)











class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the owner of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user




# @login_required
# def index(request, slug):
#     room = Room.objects.get(slug=slug)
#     messages = Message.objects.filter(room=room).order_by('created_at')
#     # public_projects = Room.objects.filter(is_private=False)
#     tasks = Task.objects.filter(room=room)

#     return render(request, 'chat/room.html', {'name': room.name, 'messages': messages, 'slug': room.slug, 'tasks': tasks})


class RoomCreateJoinView(APIView):
    permission_classes = [IsAuthenticated]
    

    def post(self, request, *args, **kwargs):
        action = request.data.get("action")
        if action == "create":
            return self.create_room(request)
        elif action == "join":
            return self.join_room(request)
        elif action == "remove_user":
            return self.remove_user_from_room(request)
        elif action == "make_admin":
            return self.make_user_admin(request)
        else:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    def create_room(self, request):
        room_name = request.data.get("room_name")
        description = request.data.get("description")
        is_private = request.data.get("is_private", False)

        if not room_name:
            return Response({"detail": "Room name is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = str(''.join(random.choices(
                string.ascii_letters + string.digits, k=4)))
            room_slug = slugify(room_name + "_" + uid)
            room = Room.objects.create(
                name=room_name,
                slug=room_slug,
                description=description,
                is_private=is_private,
                created_by=request.user
            )

            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            log = logger.error(f"Error occurred during room creation: {str(e)}")
            print(log)
            return Response({"detail": "An error occurred during room creation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def join_room(self, request):
        provided_slug = request.data.get("room_slug")
        try:
            room = Room.objects.get(slug=provided_slug)
        except Room.DoesNotExist:
            return Response({"detail": "Room does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        correct_slug = room.slug  # Actual slug for the room

        if provided_slug == correct_slug:
            # The provided slug matches the actual slug, proceed to join the room
            if not room.is_private or request.user in room.users.all():
                # Add the user to the room's users
                room.users.add(request.user)

                return Response({"detail": "Successfully joined the room."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Access denied, this is a private room!"}, status=status.HTTP_403_FORBIDDEN)
        else:
            # The provided slug does not match the actual slug
            return Response({"detail": "Invalid passcode for the room!"}, status=status.HTTP_400_BAD_REQUEST)
        
        def delete_room(self, request):
            room_slug = request.data.get("room_slug")
            try:
                room = Room.objects.get(slug=room_slug)
            except Room.DoesNotExist:
                return Response({"detail": "Room does not exist!"}, status=status.HTTP_404_NOT_FOUND)

            if room.created_by == request.user:
                room.delete()
                return Response({"detail": "Room deleted successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "You are not the creator of this room, so you cannot delete it."},
                            status=status.HTTP_403_FORBIDDEN)
        
    def remove_user_from_room(self, request):
        room_slug = request.data.get("room_slug")
        username = request.data.get("username")
        requester = request.user

        try:
            room = Room.objects.get(slug=room_slug)
        except Room.DoesNotExist:
            return Response({"detail": "Room does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(instance=room, data=request.data)
        if serializer.is_valid():
            result = serializer.remove_user(username, requester)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def make_user_admin(self, request):
        room_slug = request.data.get("room_slug")
        username = request.data.get("username")
        requester = request.user

        try:
            room = Room.objects.get(slug=room_slug)
        except Room.DoesNotExist:
            return Response({"detail": "Room does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(instance=room, data=request.data)
        if serializer.is_valid():
            result = serializer.make_admin(username, requester)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, room_slug):
        try:
            room = Room.objects.get(slug=room_slug)
            if room.is_private and request.user not in room.users.all():
                return Response({"detail": "You do not have access to this room."}, status=status.HTTP_403_FORBIDDEN)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        except Room.DoesNotExist:
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)


# class UserRoomsView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         user = request.user
#         created_rooms = user.get_created_rooms()
#         joined_rooms = user.get_joined_rooms()

#         # Now, you have the rooms created and joined by the user
#         data = {
#             'created_rooms': created_rooms.values(),
#             'joined_rooms': joined_rooms.values(),
#         }

#         return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request, room_slug):
    """Sends a message to a chat room, including media upload (optional).

    Args:
        request: The HTTP request.
        room_slug: The slug of the chat room.

    Returns:
        A JSON response with the status of the message send, or an error response if the request is invalid.
    """
    if request.method == "POST":
        # Set room and user based on the request context
        room = Room.objects.get(slug=room_slug)
        user = request.user

        # Include room and user in the request data
        request.data["room"] = room.id
        request.data["user"] = user.id

        serializer = SendMessageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Message successfully sent!"}, status=status.HTTP_201_CREATED)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid request method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_message(request, room_slug):
    """Gets all messages from a chat room.

    Args:
        request: The HTTP request.
        room_slug: The slug of the chat room.

    Returns:
        A JSON response with a list of messages, or an error response if the request is invalid.
    """
    if request.method == "GET":
        try:
            room = Room.objects.get(slug=room_slug)
            messages = Message.objects.filter(room=room).order_by("created_at")

            serialized_messages = ReceiveMessageSerializer(
                messages, many=True).data

            return Response({"messages": serialized_messages}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            raise Http404("Room does not exist!")
        except Exception as e:
            messages.error(f"Error occurred: {str(e)}")
            return HttpResponse(status=500)

    return Response({"error": "Invalid request method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        room = get_object_or_404(Room, slug=self.kwargs['room_slug'])
        serializer.save(room=room, created_by=self.request.user)

    def get_serializer_context(self):
        # Pass the room to the serializer context
        context = super().get_serializer_context()
        context['room'] = get_object_or_404(
            Room, slug=self.kwargs['room_slug'])
        return context

class RoomTasksView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = TaskSerializer

    def get_queryset(self):
        room = Room.objects.filter(slug=self.kwargs['room_slug']).first()
        room_tasks = Task.objects.filter(room=room)
        return room_tasks
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        task_id = self.kwargs["pk"]
        task_obj = Task.objects.filter(id=task_id).first()
        return task_obj
    
    def delete(self, request, *args, **kwargs):
        try:
            task_obj = self.get_object()
            task_obj.delete()
            return Response({
                "message": "task deleted"
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "message": "task not found"
            }, status=status.HTTP_404_NOT_FOUND)
    

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserNoteCreateView(generics.ListCreateAPIView):
    queryset = UserNote.objects.all()
    serializer_class = UserNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class UserNoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserNote.objects.all()
    serializer_class = UserNoteSerializer
    permission_classes = [IsAuthenticated]


class FeatureRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = FeatureRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        user_id = self.request.user.id
        return FeatureRequest.objects.filter(room=room_id, user=user_id)

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        serializer.save(room_id=room_id, user=self.request.user)


class FeatureRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeatureRequest.objects.all()
    serializer_class = FeatureRequestSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_room(request, room_slug):
    try:
        room = Room.objects.get(slug=room_slug)
        user = request.user

        if user in room.likes.all():
            room.likes.remove(user)
            return Response({"message": "Room unliked successfully."}, status=status.HTTP_200_OK)
        else:
            room.likes.add(user)
            return Response({"message": "Room liked successfully."}, status=status.HTTP_200_OK)
    except Room.DoesNotExist:
        return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SearchAPIView(APIView):
    """
    Performs a search across multiple models and returns results in JSON format.

    Requires authentication.

    Raises:
        ValueError: If the 'q' query parameter is not provided in the request.
    """
    def get(self, request):
        try:
            query = request.GET.get('q', '')
            if not query:
                raise ValueError("The 'q' parameter is required.")

            all_results = []
            all_results.extend(Room.objects.filter(Q(name__icontains=query)))
            # all_results.extend(UploadedFile.objects.filter(Q(file__icontains=query)))
            # all_results.extend(Task.objects.filter(Q(title__icontains=query)))
            # # all_results.extend(Branch.objects.filter(Q(original_file__icontains=query)))
            # all_results.extend(Message.objects.filter(Q(message__icontains=query)))

            paginator = Paginator(all_results, 25)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)

            serialized_results = []
            for result in page_obj:
                if isinstance(result, Room):
                    serialized_result = {'id': result.id, 'Room name': result.name}
                # elif isinstance(result, UploadedFile):
                #     serialized_result = {'id': result.id, 'file': result.file.name}
                # elif isinstance(result, Task):
                #     serialized_result = {'id': result.id, 'title': result.title}
                # elif isinstance(result, Branch):
                #     serialized_result = {'id': result.id, 'branch': result.original_file.file.name}
                # elif isinstance(result, Message):
                #     serialized_result = {'id': result.id, 'message': result.message}
                else:
                    serialized_result = {}
                serialized_results.append(serialized_result)

            return Response({'results': serialized_results}, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class NotificationDetail(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class MarkNotificationAsRead(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def patch(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'Notification marked as read.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_data(request):
    user = request.user

    # Retrieve rooms joined by the user
    joined_rooms = user.room_set.all()
    joined_rooms_serializer = RoomSerializer(joined_rooms, many=True)

    # Retrieve rooms created by the user
    created_rooms = user.created_rooms.all()
    created_rooms_serializer = RoomSerializer(created_rooms, many=True)

    # Retrieve tasks assigned to the user along with the room
    assigned_tasks = Task.objects.filter(assigned_to=user)
    assigned_tasks_data = TaskSerializer(assigned_tasks, many=True)

    # Serialize user data
    user_serializer = UserSerializer(user)

    # Combine all data into a single dictionary
    user_data = {
        'user': user_serializer.data,
        'joined_rooms': joined_rooms_serializer.data,
        'created_rooms': created_rooms_serializer.data,
        'assigned_tasks': assigned_tasks_data.data,
        # Add more data as needed
    }

    return Response(user_data)


class UploadFileView(APIView):
    def post(self, request, room_slug):
        try:
            room = Room.objects.get(slug=room_slug)
        except Room.DoesNotExist:
            return Response("Room not found", status=status.HTTP_404_NOT_FOUND)

        uploaded_by = request.user
        request.data['room'] = room.id
        request.data['uploaded_by'] = uploaded_by.id

        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room=room, uploaded_by=uploaded_by, is_staged=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StageFileDecisionView(APIView):
    def post(self, request, room_slug, staged_file_id):
        staged_file = File.objects.get(id=staged_file_id)
        if request.user != staged_file.uploaded_by:
            return Response("Only the uploader can make decisions on staged files", status=status.HTTP_403_FORBIDDEN)

        decision = request.data.get('decision')
        if decision == 'add':
            staged_file.is_staged = False
            staged_file.save()
            return Response("File added to room", status=status.HTTP_200_OK)
        elif decision == 'remove':
            staged_file.delete()
            return Response("File removed from staging area", status=status.HTTP_200_OK)
        else:
            return Response("Invalid decision", status=status.HTTP_400_BAD_REQUEST)


class StagedFilesView(APIView):
    def get(self, request, room_slug):
        try:
            staged_files = File.objects.filter(room__slug=room_slug, is_staged=True)
            serializer = FileSerializer(staged_files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoomFilesView(APIView):
    def get(self, request, room_slug):
        try:
            room_files = File.objects.filter(room__slug=room_slug, is_staged=False)
            serializer = FileSerializer(room_files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class UploadFileView(APIView):
#     def post(self, request, room_slug):
#         try:
#             room = Room.objects.get(slug=room_slug)
#         except Room.DoesNotExist:
#             return Response("Room not found", status=status.HTTP_404_NOT_FOUND)

#         room = Room.objects.get(slug=room_slug)
#         request.data['room'] = room.id

#         request.data['uploaded_by'] = request.user.id


#         uploaded_by = request.user
#         serializer = FileSerializer(data=request.data)
#         if serializer.is_valid():
#             uploaded_file = serializer.validated_data['path']
#             uploaded_file_hash = self.calculate_file_hash(uploaded_file)
#             existing_file = File.objects.filter(room=room, name=uploaded_file.name).first()
#             if existing_file:
#                 existing_file_hash = self.calculate_file_hash(existing_file.path)
#                 if uploaded_file_hash != existing_file_hash:
#                     serializer.save(room=room, uploaded_by=uploaded_by)
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response("File content has not changed.", status=status.HTTP_200_OK)
#             else:
#                 serializer.save(room=room, uploaded_by=uploaded_by)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def calculate_file_hash(self, file):
#         hasher = hashlib.md5()
#         for chunk in file.chunks():
#             hasher.update(chunk)
#         return hasher.hexdigest()

# class StageFileView(APIView):
#     def post(self, request, room_slug):
#         room = Room.objects.get(slug=room_slug)
#         uploaded_by = request.user
#         request.data['room'] = room.id

#         request.data['uploaded_by'] = request.user.id
#         serializer = FileSerializer(data=request.data)
#         if serializer.is_valid():
#             uploaded_file = serializer.validated_data['path']
#             serializer.save(room=room, uploaded_by=uploaded_by)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class StageFileDecisionView(APIView):
#     def post(self, request, room_slug, staged_file_id):
#         staged_file = StagedFile.objects.get(id=staged_file_id)
#         if request.user != staged_file.room.created_by:
#             return Response("Only room admin can make decisions on staged files", status=status.HTTP_403_FORBIDDEN)
        
#         decision = request.data.get('decision', None)
#         if decision == 'add':
#             staged_file.is_added = True
#             staged_file.save()
#             return Response("File added to room", status=status.HTTP_200_OK)
#         elif decision == 'remove':
#             staged_file.delete()
#             return Response("File removed from staging area", status=status.HTTP_200_OK)
#         else:
#             return Response("Invalid decision", status=status.HTTP_400_BAD_REQUEST)


# class ListStagedFilesView(APIView):
#     def get(self, request, room_slug):
#         room = Room.objects.get(slug=room_slug)
#         staged_files = StagedFile.objects.filter(room=room)
#         serializer = StagedFileSerializer(staged_files, many=True)
#         return Response(serializer.data)



# class MergeStagedFilesView(APIView):
#     def post(self, request, room_slug, branch_id):
#         room = Room.objects.get(slug=room_slug)
#         branch = Branch.objects.get(id=branch_id)
#         if request.user != room.created_by:
#             return Response("Only room admin can merge staged files", status=status.HTTP_403_FORBIDDEN)
        
#         staged_files = StagedFile.objects.filter(room=room)
#         for staged_file in staged_files:
#             if staged_file.is_added:
#                 File.objects.create(room=room, name=staged_file.file.name, path=staged_file.file.path, uploaded_by=staged_file.file.uploaded_by)
#                 staged_file.delete()
#         return Response("Staged files merged into branch", status=status.HTTP_200_OK)

# class CreateBranchView(APIView):
#     def post(self, request, room_slug):
#         room = Room.objects.get(slug=room_slug)
#         if request.user != room.created_by:
#             return Response("Only room admin can create branches", status=status.HTTP_403_FORBIDDEN)
        
#         name = request.data.get('name')
#         if not name:
#             return Response("Branch name is required", status=status.HTTP_400_BAD_REQUEST)

#         branch = Branch.objects.create(room=room, name=name)
#         return Response("Branch created successfully", status=status.HTTP_201_CREATED)


# from django.shortcuts import render
# from django.core.mail import send_mail
# from django.http import HttpResponse

# def send_email_view(request):
#     # Send an email
#     send_mail(
#         "Subject here",  # Subject
#         "Here is the message.",  # Message
#         "noahtochukwu10@gmail.com",  # From email address
#         ["noah@pario.ng"],  # To email addresses
#         fail_silently=False,  # Set it to True to suppress exceptions if email sending fails
#     )
#     return HttpResponse("Email sent successfully!")


