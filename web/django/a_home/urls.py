from django.urls import path
from .views import *

urlpatterns = [
	path('', home_view, name="home"),
	path('lobby/create/', create_lobby, name="new-lobby"),
	path('lobby/join/', join_lobby, name="join-lobby"),
	path('lobby/room/<lobby_id>', lobby_view, name="lobby"),
]
