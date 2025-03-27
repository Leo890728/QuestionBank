from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="使用者名稱",
        widget=forms.TextInput(attrs={"class": "form-control"}), 
        required=True
    )

    email = forms.EmailField(
        label="電子信箱",
        widget=forms.EmailInput(attrs={'class': 'form-control'}), 
        required=True
    )

    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
        required=True
    )

    password2 = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
        required=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class ProfileEditForm(forms.Form):
    name = forms.CharField(min_length=3, max_length=30, required=True)
    biography = forms.CharField(max_length=200, required=False)
