from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django import forms


class RegisterForm(forms.Form):
    username =  UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

    class Meta:
        model = User
        fields = ('username', 'password')



class RegistrationForm(UserCreationForm):
    username =  UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Username'})}