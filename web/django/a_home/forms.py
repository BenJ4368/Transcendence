from django.forms import ModelForm
from django import forms
from .models import *

class LobbyCreateForm(ModelForm):
	class Meta:
		model = Lobby
		fields = ['name', 'is_private']
		widgets = {
			'name' : forms.TextInput(attrs={'placeholder': 'Lobby name'}),
			'is_private' : forms.CheckboxInput(attrs={'class': 'required checkbox form-control'}),   
        }

class ChatmessageCreateForm(ModelForm):
	class Meta:
		model = LobbyMessage
		fields = ['body']
		widgets = {
			'body': forms.TextInput(attrs={
				'class': 'chat-input',
				'type': 'text',
				'name': 'message',
				'placeholder': 'Add message ...',
				'maxlength': 150,
				'autofocus': True
			})
		}