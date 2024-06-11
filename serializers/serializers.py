from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
from allauth.account.models import EmailAddress
from accounts.models import CustomUser
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse, HttpResponse

from cowork.models import (
    Room, Task, Comment,
    Message,
    File,
    # Branch,
    UserNote, FeatureRequest,
    Notification,
    StagedFile
    #   Commit, UploadedFileVersion
)

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer is for creating a new user
    """
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'username')

    # Add any extra fields you want to include in the registration form.
    extra_fields = ['first_name', 'username']

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create_user(**validated_data)
            return user
        except ValidationError as e:
            errors = {}
            for field, field_errors in e.message_dict.items():
                if field == 'username' and 'unique' in field_errors[0]:
                    errors[field] = "Username already taken."
                elif 'This field may not be blank.' in errors:
                    errors[field] = "Password is required. and should be at least 8 characters long."
                else:
                    # Add other validation errors
                     errors[field] = field_errors[0]
            raise serializers.ValidationError({
                'success': False,
                'message': errors
            })

    def to_representation(self, instance):
        """
        Transform the user instance to a response that includes success message
        """
        return {
            "success": True,
            "message": "Account created successfully",
            "data": {
                "email": instance.email,
                "first_name": instance.first_name,
                "username": instance.username
            }
        }


class SignInSerializer(serializers.Serializer):
    """
    Serializer for signing in
    """

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs: dict):
        """
        This is for validating credentiials for signing in
        """

        user = User.objects.filter(email=attrs["email"]).first()
        
        if (user is None):
            raise serializers.ValidationError({
                "sucess": "false",
                "message": "user doesn't exist"
            })
        
        if user and not user.check_password(attrs["password"]):
            raise serializers.ValidationError({
                    "success": "false",
                    "message": "Invalid Password"
                }
            ) 
        
        return attrs
        

class ChangePasswordSerializer(serializers.Serializer):
    """This serializer is for changing a user's password"""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context["request"].user

        if check_password(attrs["old_password"], user.password) is False:
            raise serializers.ValidationError({
                "old_password": "Please recheck the old password"
            })

        elif attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Please confirm the new password"
            })

        return attrs

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")

class UserSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()
    created_rooms = serializers.SerializerMethodField()
    # Add more fields as needed

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'rooms', 'created_rooms')

    def get_rooms(self, user):
        rooms = user.room_set.all()
        return RoomSerializer(rooms, many=True).data

    def get_created_rooms(self, user):
        created_rooms = user.created_rooms.all()
        return RoomSerializer(created_rooms, many=True).data




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
        queryset=CustomUser.objects.all(),
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


class ProfileSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username'
        ]


    def validate(self, attrs):
        return super().validate(attrs)
    

    def update(self, instance, validated_data):
        """Updates user profile"""

        return super().update(instance, validated_data)
    


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'room', 'sender', 'message', 'timestamp', 'is_read']
