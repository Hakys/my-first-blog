from django import forms
from .models import Product, Imagen, Externo

class ExternoForm(forms.ModelForm):
    class Meta:
        model = Externo
        fields = ('name', 'url', 'file',)