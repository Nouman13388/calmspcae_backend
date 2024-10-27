import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from my_app.routing import websocket_urlpatterns  # Adjust according to your routing setup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmspcae_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
