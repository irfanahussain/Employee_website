from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'autofocus': True, 'placeholder': 'Username or email',
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Password', 'id': 'id_password',
        }),
    )
    remember_me = forms.BooleanField(
        label='Remember me', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    intended_role = forms.CharField(required=False, widget=forms.HiddenInput())

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Please enter a correct username/email and password. Note that both fields may be case-sensitive.",
    }


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


class StyledPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
    )


class StyledSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
