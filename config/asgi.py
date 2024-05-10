import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from decouple import config


os.environ['DJANGO_SETTINGS_MODULE'] = config('DJANGO_SETTINGS_MODULE', default='config.settings.dev')

from coloby.cowork import routing


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    "websocket":AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})
