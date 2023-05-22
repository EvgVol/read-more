from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class LoginForm(forms.Form):
    """Форма входа в систему."""

    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    """Форма для регистрации новых пользователей."""

    privacy_policy = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'privacy_policy',)

    def clean_username(self):
        """Проверка на допустимые символы в имени пользователя."""
        username = self.cleaned_data.get('username')
        if not username.isalnum():
            raise ValidationError(_('Имя пользователя должно содержать только буквы и цифры'), code='invalid_character')
        return username

    def clean(self):
        """Проверка на заполнение всех полей формы."""
        cleaned_data = super().clean()
        privacy_policy = cleaned_data.get('privacy_policy')
        
        if not privacy_policy:
            self.add_error('privacy_policy', 'Необходимо согласие с политикой конфиденциальности')

        for field_name in cleaned_data:
            if not cleaned_data[field_name]:
                self.add_error(field_name, f'Поле {field_name} обязательно для заполнения')
        
        return cleaned_data