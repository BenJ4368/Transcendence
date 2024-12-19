from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from django.db import transaction
import json
import logging
from .models import *

class LobbyConsumer(WebsocketConsumer):

	def connect(self):
		self.user = self.scope['user']
		self.lobby_id = self.scope['url_route']['kwargs']['lobby_id'] 
		self.lobby = get_object_or_404(Lobby, lobby_id=self.lobby_id)

		async_to_sync(self.channel_layer.group_add)(
			self.lobby_id, self.channel_name
		)


		async_to_sync(self.channel_layer.group_send)(self.lobby_id, {'type':'update_lobby'})
		self.accept()

	def disconnect(self, close_code):

		if self.lobby == None:
			return

		async_to_sync(self.channel_layer.group_discard)(
			self.lobby_id, self.channel_name
		)
		# Vérifie si l'utilisateur est l'admin du lobby
		if self.scope['user'] == self.lobby.admin:
			# Envoie un message à tous les membres pour qu'ils quittent
			async_to_sync(self.channel_layer.group_send)(
				self.lobby_id,
				{
					"type": "admin_left",
					"message": "Lobby closed by admin. Redirecting to home.",
				}
			)
			print(f"Lobby ID: {self.lobby.name}")
			print(f"Lobby ID: {self.lobby.id}")
			print(f"Lobby Admin: {self.lobby.admin}")
			print(f"Lobby Members: {list(self.lobby.members.all())}")
			try:
				with transaction.atomic():
					self.lobby.delete()
				print("Lobby supprimé avec succès")
			except Exception as e:
				print(f"Erreur lors de la suppression du lobby : {e}")
			return


		if self.lobby:
			self.lobby.members.remove(self.user)  # Retirer l'utilisateur du groupe dans le modèle
			self.lobby.save()
		
		async_to_sync(self.channel_layer.group_send)(self.lobby_id, {'type':'update_lobby'})


	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		body = text_data_json['body']
		
		message = LobbyMessage.objects.create(
			body = body,
			author = self.user, 
			lobby = self.lobby 
		)
		event = {
			'type': 'message_handler',
			'message_id': message.id,
		}
		async_to_sync(self.channel_layer.group_send)(
			self.lobby_id, event
		)


	def message_handler(self, event):
		message_id = event['message_id']
		message = LobbyMessage.objects.get(id=message_id)

		context = {
			'message': message,
			'user': self.user,
			'lobby': self.lobby
		}

		response_data = {
			'type': 'chat_message',
			'content': render_to_string("a_home/partials/chat_message_p.html", context=context)
		}
		
		self.send(text_data=json.dumps(response_data))

	def update_lobby(self, event):
		
		is_launchable = self.lobby.members.count() == 2
		players = self.lobby.members.all()  # Ou une liste personnalisée


		context = {
			'player_1': players[0] if len(players) > 0 else None,
			'player_2': players[1] if len(players) > 1 else None,
			'lobby': self.lobby,
		}

		response_data = {
			'type': 'update_message',
			'is_launchable': is_launchable,
			'content': render_to_string("a_home/partials/players.html", context=context),
		}

		self.send(text_data=json.dumps(response_data))


	# Méthode appelée pour gérer le message envoyé aux membres
	def admin_left(self, event):
		
		self.lobby = None
		self.send(text_data=json.dumps({
			"type": "redirect",
			"message": event["message"],
		}))



class GlobalConsumer(WebsocketConsumer):
	def connect(self):
		# Créer ou rejoindre un groupe global
		self.user = self.scope['user']
		self.group_name = 'global_group'
		async_to_sync(self.channel_layer.group_add)(
			self.group_name,
			self.channel_name
		)
		self.accept()

	def disconnect(self, close_code):
		# Quitter le groupe global
		async_to_sync(self.channel_layer.group_discard)(
			self.group_name,
			self.channel_name
		)

	def receive(self, text_data):
		# Traiter les messages reçus du client
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		sender = getattr(self, 'user', 'Inconnu')
		full_message = f"{sender}: {message}"

		# Envoyer un message à tous les membres du groupe
		async_to_sync(self.channel_layer.group_send)(
			self.group_name,
			{
				'type': 'global_message',
				'message': full_message
			}
		)

	def global_message(self, event):
		# Recevoir un message du groupe
		message = event['message']

		# Envoyer le message au WebSocket
		self.send(text_data=json.dumps({
			'message': message
		}))