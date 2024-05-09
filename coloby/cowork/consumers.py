import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from coloby.cowork.models import Room, Message, Task
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = None
        self.user = None

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_slug"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        self.room = await self.get_or_create_room(self.room_name)
        
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        
        await self.add_user_to_room(self.room, self.user)
        await self.accept()

    async def disconnect(self, close_code):
        await self.remove_user_from_room(self.room, self.user)
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = self.user.username

        await self.save_message(self.room, self.user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        message_html = f"{message}"
        await self.send(
            text_data=json.dumps(
                {
                    "message": message_html,
                    "username": username
                }
            )
        )

    @sync_to_async
    def save_message(self, room, user, message):
        Message.objects.create(room=room, user=user, message=message)

    @sync_to_async
    def get_or_create_room(self, slug):
        return get_object_or_404(Room, slug=slug)

    @sync_to_async
    def add_user_to_room(self, room, user):
        if user not in room.users.all():
            room.users.add(user)
            room.save()

    @sync_to_async
    def remove_user_from_room(self, room, user):
        if user in room.users.all():
            room.users.remove(user)
            room.save()




class NotificationConsumer(AsyncWebsocketConsumer):
    """
    A Django Channels consumer that handles various types of notifications
    within a specific room.

    This consumer allows clients to connect to a room and receive real-time
    updates about messages, file uploads, branch activities, and tasks.

    Attributes:
        room_name: The name of the room the consumer is connected to.
        room_group_name: The name of the Channel group used for broadcasting
                        notifications to the room.

    Methods:
        connect(self):
            Accepts the connection and joins the room group.
        disconnect(self, close_code):
            Leaves the room group when the connection is closed.
        receive(self, text_data):
            Handles incoming messages containing notification data.
                - Parses received JSON data.
                - Validates notification type (`message`, `file_upload`,
                  `branch_activity`, or `task`).
                - Saves the notification data to the database.
                - Prepares a notification response with data and timestamp.
                - Broadcasts the notification to the room group.
                - Handles potential errors.
        send_notification(self, event):
            Sends the received notification data to the connected client.
        send_error_response(self, error_message):
            Sends an error response message to the connected client.
    """
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'room_{self.room_name}'

        # Joins room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leaves room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            notification_type = data.get('type')

            if notification_type == 'message':
                message_text = data.get('message')
                sender_id = data.get('sender_id')
                timestamp = timezone.now()

                # Saves message to the database
                message = Message.objects.create(
                    room_id=self.room_name,
                    sender_id=sender_id,
                    message=message_text,
                    timestamp=timestamp
                )

                # Prepares notification response
                notification = {
                    'type': 'message',
                    'message': message_text,
                    'sender_id': sender_id,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }

            # elif notification_type == 'file_upload':
            #     file_name = data.get('file_name')
            #     uploader_id = data.get('uploader_id')
            #     timestamp = timezone.now()

            #     # Saves file upload activity to the database
            #     uploaded_file = UploadedFile.objects.create(
            #         room_id=self.room_name,
            #         uploader_id=uploader_id,
            #         file_name=file_name,
            #         timestamp=timestamp
            #     )

            #     # Prepares notification response
            #     notification = {
            #         'type': 'file_upload',
            #         'file_name': file_name,
            #         'uploader_id': uploader_id,
            #         'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            #     }

            # elif notification_type == 'branch_activity':
            #     branch_name = data.get('branch_name')
            #     actor_id = data.get('actor_id')
            #     timestamp = timezone.now()

            #     # Saves branch activity to the database
            #     branch = Branch.objects.create(
            #         room_id=self.room_name,
            #         actor_id=actor_id,
            #         branch_name=branch_name,
            #         timestamp=timestamp
            #     )

            #     # Prepares notification response
            #     notification = {
            #         'type': 'branch_activity',
            #         'branch_name': branch_name,
            #         'actor_id': actor_id,
            #         'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            #     }

            elif notification_type == 'task':
                task_title = data.get('task_title')
                creator_id = data.get('creator_id')
                timestamp = timezone.now()

                # Saves task to the database
                task = Task.objects.create(
                    room_id=self.room_name,
                    creator_id=creator_id,
                    title=task_title,
                    timestamp=timestamp
                )

                # Prepares notification response
                notification = {
                    'type': 'task',
                    'task_title': task_title,
                    'creator_id': creator_id,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }

            # Broadcasts the notification(s) to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_notification',
                    'notification': notification
                }
            )
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            await self.send_error_response(error_message)

    async def send_notification(self, event):
        notification = event['notification']
        # Sends notification to WebSocket (Channels)
        await self.send(text_data=json.dumps(notification))

    async def send_error_response(self, error_message):
        # Sends error response to WebSocket (Channels)
        response = {
            'type': 'error',
            'error_message': error_message
        }
        await self.send(text_data=json.dumps(response))