from django import forms

from .models import Comment


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
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    """Форма поиска"""

    query = forms.CharField()
