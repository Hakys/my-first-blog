from django import forms
from django.contrib.auth.models import User
from .models import *

class ExternoForm(forms.ModelForm):
    class Meta:
        model = Externo
        fields = ('name', 'url', 'file',)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')