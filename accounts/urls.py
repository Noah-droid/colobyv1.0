from django.urls import path
from django.contrib.auth import views as auth_views
import accounts.views as user_views
from accounts.views import (
    UserRegistrationView,
    LogoutView, 
    GoogleLogin, 
    SignInAPIView, 
    ChangePasswordView,
    UpdateUserProfileView,
    RefreshAccessTokenAPIView,
)
from . import views


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    
    path("log-in/", SignInAPIView.as_view(), name="log_in"),
    path("update-profile/<uuid:id>/", UpdateUserProfileView.as_view(), name="update_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
    path('refresh-token/', RefreshAccessTokenAPIView.as_view(), name='refresh-token'),
    path('log-out/', LogoutView.as_view(), name="log-out"),

    # OAUTH LOGINS
    path("google-login/", GoogleLogin.as_view(), name="google-login"),

]

