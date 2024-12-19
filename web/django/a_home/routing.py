from django.urls import path
from .consumers import *

websocket_urlpatterns = [
	path("ws/lobby/<lobby_id>", LobbyConsumer.as_asgi()),
	path('ws/global/', GlobalConsumer.as_asgi()),
]