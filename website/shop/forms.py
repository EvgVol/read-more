from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'description',
                  'price', 'available']
        labels = {
            'name': 'Заголовок',
            'description': 'Описание',
            'price': 'Цена',
            'category': 'Категория',
            'image': 'Изображение',
            'available': 'В наличии',
        }
