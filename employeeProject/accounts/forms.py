from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['phone','address','emergency_contact','profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control','rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class':'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class':'form-control'}),
        }
