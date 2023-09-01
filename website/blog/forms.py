from django import forms
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from .models import Comment, Post

User = get_user_model()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'category', 'tags',  'image']
        labels = {
            'title': 'Заголовок',
            'body': 'Контент',
            'tags': 'Теги',
            'category': 'Категория',
            'image': 'Изображение',
        }


class EmailPostForm(forms.Form):
    """Форма по отправки постов по электронной почте."""

    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    """Форма по добавлению комментариев к посту."""

    class Meta:
        model = Comment
        fields = ['author', 'body']


class SearchForm(forms.Form):
    """Форма поиска"""

    query = forms.CharField()
