from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'password']

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Correo")