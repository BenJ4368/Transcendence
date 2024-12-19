from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile

from django.core.exceptions import ValidationError
import re

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ['image', 'displayname', 'info' ]
		widgets = {
			'image': forms.FileInput(),
			'displayname' : forms.TextInput(attrs={'placeholder': 'Add display name'}),
			'info' : forms.Textarea(attrs={'rows':3, 'placeholder': 'Add information'})
		}

class EmailForm(ModelForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ['email']


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'input-box'})
    )
    password = forms.CharField(
        min_length=8,
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-box'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'e-mail@gmail.com', 'class': 'input-box'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if '@' not in email:
            raise ValidationError('Email not valid')

        pattern = r'\.[a-zA-Z]{2,}$'
        if not re.search(pattern, email):
            raise ValidationError('Email not valid')
        
        return email