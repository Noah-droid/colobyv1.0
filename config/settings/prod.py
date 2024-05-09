from .dev import *



database_url = config("DATABASE_URL")
DATABASES["default"] = dj_database_url.parse(database_url)


# EMAIL SETTINGS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
# DEFAULT_FROM_EMAIL = 'admin@coloby.com'
EMAIL_SUBJECT_PREFIX = '[Coloby]'
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False




CORS_ORIGIN_ALLOW_ALL = config('CORS_ORIGIN_ALLOW_ALL', default=False, cast=bool)
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in config('CORS_ALLOWED_ORIGINS').split(',')]
CORS_ALLOW_METHODS = [method.strip() for method in config('CORS_ALLOW_METHODS').split(',')]
CORS_ALLOW_HEADERS = [header.strip() for header in config('CORS_ALLOW_HEADERS').split(',')]
