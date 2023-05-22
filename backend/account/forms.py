from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginForm(forms.Form):
    """Форма входа в систему."""

    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    """Форма для регистрации новых пользователей."""

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')