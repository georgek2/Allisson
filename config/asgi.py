# config/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import your WebSocket consumer
from api.consumers import TaskConsumer

application = ProtocolTypeRouter({
    # Regular HTTP requests → Django
    "http": get_asgi_application(),

    # WebSocket connections → Channels
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/tasks/", TaskConsumer.as_asgi()),
        ])
    ),
})

