import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_application = get_asgi_application()

from apps.conversations.routing import websocket_urlpatterns
from config.websocket_auth import JWTAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
