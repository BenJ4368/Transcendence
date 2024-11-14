from django import forms
from django.core.exceptions import ValidationError
import re


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