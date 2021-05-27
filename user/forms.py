from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
            'email': None,
            'password1': None,
            'password2': None,
        }


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
