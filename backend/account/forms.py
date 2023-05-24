from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm

from core.mixins import RequiredFieldsMixin


User = get_user_model()


class LoginForm(forms.Form):
    """Форма входа в систему."""

    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    """Форма для регистрации новых пользователей."""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    privacy_policy = forms.BooleanField(required=True, error_messages={
        'required': 'Вы должны согласиться с политикой конфиденциальности',
    })

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'privacy_policy']


class UserEditForm(ModelForm):
    """Форма редактирования данных пользователя."""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                 'last_name', 'birthdate', 'avatar',
                'phone_number', 'about_me']


# class ProfileUpdateForm(ModelForm):
#     """Форма обновления данных пользователя."""

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name',
#                   'last_name', 'birthdate', 'avatar',
#                   'phone_number')

#     def __init__(self, *args, **kwargs):
#         """Обновление стилей формы под bootstrap."""
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({
#                 'class': 'form-control',
#                 'autocomplete': 'off'
#             })

#     def get_object(self, queryset=None):
#         return self.request.user.profile

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         user = User.objects.filter(username__iexact=username).exclude(username=username).exists()
#         if user:
#             raise ValidationError("Пользователь с таким именем уже существует.")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         username = self.cleaned_data.get('username')
#         user = User.objects.filter(email__iexact=email).exclude(username=username).exists()
#         if user:
#             raise ValidationError("Пользователь с таким email уже существует.")
#         return email

#     def clean_phone_number(self):
#         phone_number = self.cleaned_data.get('phone_number')
#         username = self.cleaned_data.get('username')
#         user = User.objects.filter(phone_number__iexact=phone_number).exclude(username=username).exists()
#         if user:
#             raise ValidationError("Пользователь с таким номером телефона уже существует.")
#         return phone_number