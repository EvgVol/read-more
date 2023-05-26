import requests

from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image


class ImageCreateForm(forms.ModelForm):
    """Форма добавления новых изображений."""
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput
        }

    def clean_url(self):
        # Получаем URL-адрес из формы
        url = self.cleaned_data['url']
        # Список допустимых расширений файлов изображений
        valid_extensions = ['jpg', 'jpeg', 'png']
        # Получаем расширение файла из URL-адреса и переводим его в нижний регистр
        extension = url.rsplit('.', 1)[1].lower()
        # Если расширение недействительное, вызываем ValidationError
        if extension not in valid_extensions:
            raise forms.ValidationError(
                'Указанный URL-адрес не соответствует допустимым '
                'расширениям изображений.')
        # Возвращаем проверенный URL-адрес
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        # Создаем базовый объект модели Image из формы
        image = super().save(commit=False)
        # Получаем URL-адрес изображения из формы
        image_url = self.cleaned_data['url']
        # Генерируем уникальное имя файла изображения на основе заголовка
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        # Загружаем изображение из интернета и сохраняем его под уникальным именем
        response = requests.get(image_url)
        image.image.save(image_name, ContentFile(response.content), save=False)
        # Сохраняем объект модели Image
        if commit:
            image.save()
        return image
