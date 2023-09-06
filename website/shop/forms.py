from django import forms
from django.forms.models import inlineformset_factory

from .models import Product, ProductImage


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


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage
        fields = '__all__'


ProductImageFormSet = inlineformset_factory(Product,
                                            ProductImage,
                                            form=ProductImageForm,
                                            extra=1,
                                            max_num=10,
                                            min_num=1,
                                            can_delete=True)
