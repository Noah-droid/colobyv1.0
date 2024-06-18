from django.utils.deprecation import MiddlewareMixin

class TokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        access_token = request.COOKIES.get('auth_token')

        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        elif refresh_token:
            # Optional: Handle token refresh logic here if needed
            pass
