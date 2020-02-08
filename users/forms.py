from django import forms
from .models import profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    address = forms.CharField(max_length=300)
    phone = forms.CharField(max_length=20)

    class Meta:
        model = profile
        fields = ['image', 'address', 'phone']
