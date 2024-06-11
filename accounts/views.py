from rest_framework import status, generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from serializers.serializers import (
    UserRegistrationSerializer, 
    SignInSerializer, 
    ChangePasswordSerializer,
    ProfileSerializer,
)
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.authtoken.models import Token
from utils.utils import generate_token_lifetime
from utils.constants import ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from datetime import timedelta


from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class SignInAPIView(generics.GenericAPIView):
    serializer_class = SignInSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True): 

            user = User.objects.filter(email=serializer.validated_data['email']).first()
            user_refresh_token = RefreshToken.for_user(user)

            # This sets refresh and access_token of a user to cookies 
            return self.set_tokens_to_cookies(user_refresh_token)

    
    def set_tokens_to_cookies(self, user_refresh_token):
        """set user refresh and access token to cookies"""
        response = HttpResponse(status=200)
        
        response.set_cookie('refresh_token', 
                            str(user_refresh_token), 
                            httponly=True, 
                            samesite="Lax", 
                            expires=generate_token_lifetime(REFRESH_TOKEN_LIFETIME), 
                            max_age=timedelta(REFRESH_TOKEN_LIFETIME))
        
        response.set_cookie('auth_token', 
                            str(user_refresh_token.access_token), 
                            httponly=True, 
                            samesite="Lax", 
                            expires=generate_token_lifetime(ACCESS_TOKEN_LIFETIME), 
                            max_age=timedelta(ACCESS_TOKEN_LIFETIME))
        
        return response


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            user.set_password(serializer.validated_data["confirm_new_password"])   
            user.save()         
            return Response({
                "message": "password changed successfully"
            }, status=status.HTTP_200_OK)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3001/"
    client_class = OAuth2Client


    def dispatch(self, request, *args, **kwargs):
        """
           Overriding the dispatch method to customize the response:
            - Remove the temporary 'key' generated during authentication.
            - Create an access token for the authenticated user and add it to the response.
            This approach is used as we are not using Token-based authentication.
        """
        response = super().dispatch(request, *args, **kwargs) # Access the response returned by complete_login method
        key = response.data['key']
        user_id_associated_with_token = Token.objects.filter(key=key).first().user.id
        user = User.objects.filter(id=user_id_associated_with_token).first()
        response.data.pop('key')
        response.data['access_token'] = str(RefreshToken.for_user(user).access_token)
        
        return response
   


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    http_method_names = ["get", "put"]
    
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    

class RefreshAccessTokenAPIView(TokenRefreshView):
    """Inheriting class for refreshing access token"""

    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)
