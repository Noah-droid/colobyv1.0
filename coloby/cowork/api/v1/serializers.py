from rest_framework import serializers

from coloby.cowork.models import (
    Room, Task, Comment,
    Message,
    File,
    # Branch,
    UserNote, FeatureRequest,
    Notification,
    StagedFile
    #   Commit, UploadedFileVersion
)


from django.contrib.auth import get_user_model


User = get_user_model()



class RoomSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    total_users = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = "__all__"

    def get_users(self, room):
        return room.users.values_list('username', flat=True)

    def get_created_by(self, room):
        return room.created_by.username if room.created_by else None

    def get_total_users(self, room):
        return room.users.count()

    def remove_user(self, username, requester):
        if requester == self.instance.created_by:
            user_to_remove = self.instance.users.filter(username=username).first()
            if user_to_remove:
                self.instance.users.remove(user_to_remove)
                return {"detail": f"User {username} removed from the room."}
            else:
                return {"detail": "User not found in the room."}
        else:
            return {"detail": "Only the room creator can remove users."}

    def make_admin(self, username, requester):
        if requester == self.instance.created_by:
            user_to_make_admin = self.instance.users.filter(username=username).first()
            if user_to_make_admin:
                user_to_make_admin.is_admin = True
                user_to_make_admin.save()
                return {"detail": f"User {username} is now an admin of the room."}
            else:
                return {"detail": "User not found in the room."}
        else:
            return {"detail": "Only the room creator can make users admins."}





class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'room', 'name', 'path', 'uploaded_by', 'is_staged', 'uploaded_at']



class StagedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StagedFile
        fields = ['id', 'room', 'uploaded_by', 'file', 'is_staged', 'is_added_to_room']

class UserNoteSerializer(serializers.Serializer):
    class Meta:
        model = UserNote
        fields = "__all__"


class FeatureRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureRequest
        fields = '__all__'
        read_only_fields = ('room', 'user')


class SendMessageSerializer(serializers.ModelSerializer):
    media_file = serializers.FileField(allow_empty_file=True, required=False)

    class Meta:
        model = Message
        fields = "__all__"

    def create(self, validated_data):
        media_file = validated_data.pop("media_file", None)
        message = Message.objects.create(**validated_data)

        if media_file:
            message.media = media_file
            message.save()

        return message


class ReceiveMessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Message
        fields = ["user", "message", "media", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )
    due_date = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Task
        exclude = ['created_by']  # Exclude created_by field from user input
        read_only_fields = ['room']

    def validate_assigned_to(self, value):
        # Access the room and creator from the context
        room = self.context['room']
        creator = room.created_by

        # Check if the assigned user is a member of the room (excluding the creator)
        if not (room.users.filter(id=value.id).exists() or value == creator):
            raise serializers.ValidationError(
                "The assigned user must be a member of the room or the room creator.")

        return value



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'room', 'sender', 'message', 'timestamp', 'is_read']
