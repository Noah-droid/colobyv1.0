from rest_framework import status, generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from serializers.serializers import (
    UserRegistrationSerializer, 
    SignInSerializer, 
    ChangePasswordSerializer,
    UpdateUserProfileSerializer,
)
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

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
            return Response(serializer.data)
        

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
   
    

class LogoutView(APIView):
    """
        This endpoint is for logging out a user 
    """
    def post(self, request):

        # NOTE: This only logs out a user that logs in using OAUTH for now
        user_token = request.data["token"]
        token = Token.objects.filter(key=user_token).first()
        if token:
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                "error":"invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)
    


class UpdateUserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserProfileSerializer
    http_method_names = ["get", "put"]
    
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    

class RefreshAccessTokenAPIView(TokenRefreshView):
    """Inheriting class for refreshing access token"""

    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)