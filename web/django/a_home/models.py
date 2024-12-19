from django.db import models
from django.contrib.auth.models import User
import shortuuid

class Lobby(models.Model):
	lobby_id = models.CharField(max_length=128, unique=True, default=shortuuid.uuid)
	name = models.CharField(max_length=128, null=True , blank=True)
	admin = models.ForeignKey(User, related_name='my_lobby', blank=True, null=True, on_delete=models.SET_NULL)
	members = models.ManyToManyField(User, blank=True)
	max_members = models.PositiveIntegerField(default=2)
	is_private = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	def is_full(self):
		return self.members.count() >= self.max_members


	def delete(self, *args, **kwargs):
		print(f"Début suppression du Lobby {self.lobby_id}")
		print(f"Admin : {self.admin}")
		print(f"Membres : {self.members.all()}")
		self.members.clear()
		print("Les membres ont été nettoyés.")
		super().delete(*args, **kwargs)
		print(f"Lobby {self.lobby_id} supprimé.")


class LobbyMessage(models.Model):
	lobby = models.ForeignKey(Lobby, related_name='lobby_messages', on_delete=models.CASCADE)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	body = models.CharField(max_length=300)
	created = models.DateTimeField(auto_now_add=True)
		
	def __str__(self):
		return f'{self.author.username} : {self.body}'
	
	class Meta:
		ordering = ['-created']