from django.forms import forms

from .views import Product


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
