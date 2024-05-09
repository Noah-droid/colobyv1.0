from django.urls import path
from coloby.accounts.api.v1.views import (
    RegisterView,
    GoogleLogin, 
    SignInAPIView, 
    ChangePasswordView,
    UpdateUserProfileView,
    RefreshAccessTokenAPIView,
)



urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    
    path("log-in/", SignInAPIView.as_view(), name="log_in"),
    path("update-profile/", UpdateUserProfileView.as_view(), name="update_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path('refresh-token/', RefreshAccessTokenAPIView.as_view(), name='refresh-token'),

    # OAUTH LOGINS
    path("google-login/", GoogleLogin.as_view(), name="google-login"),

]

