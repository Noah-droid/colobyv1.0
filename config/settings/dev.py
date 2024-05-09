from .base import *


THIRD_PARTY_APPS = [
    "channels",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "rest_framework_swagger",
    "drf_yasg",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "tinymce",
    "dj_rest_auth",
    "dj_rest_auth.registration",
]

LOCAL_APPS = [
    "coloby.accounts",
    "coloby.cowork", 
]


INSTALLED_APPS +=  THIRD_PARTY_APPS + LOCAL_APPS 


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


# SIMPLEJWT SETTINGS

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=50),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "SLIDING_TOKEN_LIFETIME": timedelta(days=60),
    "SLIDING_TOKEN_REFRESH_LIFETIME_GRACE_PERIOD": timedelta(days=1),
    "SLIDING_TOKEN_REFRESH_LIFETIME_ALLOWANCE": timedelta(days=1),
    "SLIDING_TOKEN_REFRESH_AFTER_LIFETIME": timedelta(days=1),
    "SLIDING_TOKEN_LIFETIME_GRACE_PERIOD": timedelta(days=1),
    "SLIDING_TOKEN_SAVE_BODY": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
}


CHANNEL_LAYERS = {
    'default': {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


# SOCIAL_LOGIN_SETTINGS
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config('CLIENT_ID'),  
            "secret": config('CLIENT_SECRET'),                                     
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "VERIFIED_EMAIL": True,
    },
}




EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# # DEBUG_TOOLBAR_SETTINGS

# INTERNAL_IPS = [
#     "127.0.0.1",
#     "localhost",
#     "coloby.onrender.com"
# ]




# OAUTH SETTINGS
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_GET = True
