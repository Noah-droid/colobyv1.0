from rest_framework import serializers
from allauth.account.models import EmailAddress
from accounts.models import CustomUser
from django.contrib.auth.hashers import check_password

from cowork.models import (
    Room, Task, Comment,
      Message, UploadedFile, 
      Branch, UserNote, FeatureRequest)

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
        Serializer is for creating a new user
    """
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 
            'first_name', 
            'last_name', 
            'password', 
            'username'
            ]
        
    def validate(self, attrs):
        return super().validate(attrs)
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user 

class SignInSerializer(serializers.Serializer):
    """
    Serializer for signing in a user
    """
    
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    def validate(self, attrs: dict):
        """
        This is for validating credentials for signing in
        """
        error_messages = {
             "error-mssg-1": {
                "credential_error": "Please recheck the credentials provided."
            },
        }
        
        user = User.objects.filter(email=attrs["email"]).first()
        if user:
            if user.check_password(attrs["password"]):
                return user
            else: # This raises error if the password provided is wrong
                raise serializers.ValidationError(error_messages["error-mssg-1"])
        else: # This raises error if the user doesn't exist
            raise serializers.ValidationError(error_messages["error-mssg-1"])
        
    def to_representation(self, user):
        username =  User.objects.get(email=user).username
        refresh = RefreshToken.for_user(user)
        return {"Info": f"Welcome {username}", "access_token": str(refresh.access_token)}


class ChangePasswordSerializer(serializers.Serializer):
    """This serializer is for changing a user's password"""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context["request"].user
        
        if check_password(attrs["old_password"], user.password) is False:
            raise serializers.ValidationError({
                            "old_password":"Please recheck the old password"
                            })
    
        elif attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({
                "confirm_password":"Please confirm the new password"
                })
        
        return attrs
    
    
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password")
    
class RoomSerializer(serializers.ModelSerializer):
    users = CustomUserSerializer(many=True)
    created_by = CustomUserSerializer()
    class Meta:
        model = Room
        fields = "__all__"


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
    class Meta:
        model = Message
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['room'].required = True
        self.fields['user'].required = True
        self.fields['message'].required = True

class ReceiveMessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Message
        fields = ["user", "message", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class UploadedFileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="uploaded_by.username")
    access_permissions = serializers.StringRelatedField(many=True)
    class Meta:
        model = UploadedFile
        fields = ["file", "description", "owner", "access_permissions", "file_size"]


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['original_file', 'content', 'description']


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
        'first_name',
        'email',
        'last_name',
        'username'
        ]

    def validate(self, attrs):
        return super().validate(attrs)
    
