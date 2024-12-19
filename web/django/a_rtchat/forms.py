from django.forms import ModelForm
from django import forms
from .models import *

class ChatmessageCreateForm(ModelForm):
	class Meta:
		model = GroupMessage
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

class NewGroupForm(ModelForm):
	class Meta:
		model = ChatGroup
		fields = ['groupchat_name']
		widgets = {
			'body': forms.TextInput(attrs={
				'class': 'text-input',
				'type': 'text',
				'name': 'message',
				'placeholder': 'Chatgroup Name...',
				'maxlength': 150,
				'autofocus': True
			})
		}

class ChatRoomEditForm(ModelForm):
	class Meta:
		model = ChatGroup
		fields = ['groupchat_name']
		widgets = {
			'body': forms.TextInput(attrs={
				'class': 'text-input',
				'type': 'text',
				'name': 'message',
				'placeholder': 'Chatgroup Name...',
				'maxlength': 150,
				'autofocus': True
			})
		}


