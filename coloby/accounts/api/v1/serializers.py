from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from coloby.cowork.api.v1.serializers import RoomSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer is for creating a new user
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'username')

    # Add any extra fields you want to include in the registration form.
    extra_fields = ['first_name', 'username']

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
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
    password = serializers.CharField(required=True)

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

        elif (user and user.check_password(attrs["password"])):
            return user

        else:
            raise serializers.ValidationError({
                "sucess": "false",
                "message": "Invalid credentials"
            })

    def to_representation(self, instance):
        user = User.objects.get(email=instance.email)
        refresh = RefreshToken.for_user(instance)
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "user_id": user.id
        }


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




class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username'
        ]

    def validate(self, attrs):
        return super().validate(attrs)
    



class UserSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()
    created_rooms = serializers.SerializerMethodField()
    # Add more fields as needed

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'rooms', 'created_rooms')

    def get_rooms(self, user):
        rooms = user.room_set.all()
        return RoomSerializer(rooms, many=True).data

    def get_created_rooms(self, user):
        created_rooms = user.created_rooms.all()
        return RoomSerializer(created_rooms, many=True).data

