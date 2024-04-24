import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey

logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Check headers
        api_key = request.headers.get('Authorization')
        if api_key:
            try:
                key = api_key.split(' ')[1]  # Extract the API key from the Authorization header
                api_key_obj = APIKey.objects.get(key=key)
                logger.info(f'User {api_key_obj.user.username} authenticated successfully with API key from headers: {api_key_obj.key}')
                return (api_key_obj.user, api_key_obj)
            except (IndexError, APIKey.DoesNotExist):
                logger.warning('Invalid API key provided in the request headers.')
                pass

        # Check query parameters
        api_key = request.query_params.get('api_key')
        if api_key:
            try:
                api_key_obj = APIKey.objects.get(key=api_key)
                logger.info(f'User {api_key_obj.user.username} authenticated successfully with API key from query parameters: {api_key_obj.key}')
                return (api_key_obj.user, api_key_obj)
            except APIKey.DoesNotExist:
                logger.warning('Invalid API key provided in the query parameters.')
                pass

        # Check request body (if it's sent as JSON)
        api_key = request.data.get('api_key')
        if api_key:
            try:
                api_key_obj = APIKey.objects.get(key=api_key)
                logger.info(f'User {api_key_obj.user.username} authenticated successfully with API key from request body: {api_key_obj.key}')
                return (api_key_obj.user, api_key_obj)
            except APIKey.DoesNotExist:
                logger.warning('Invalid API key provided in the request body.')
                pass

        # No API key found in headers, query parameters, or request body
        logger.warning('No API key provided in the request.')
        return None

