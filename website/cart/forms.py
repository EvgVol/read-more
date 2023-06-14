from django import forms

from shop.models import Product


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    """Форма добавление товаров в корзину."""

    product_id = forms.IntegerField()
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES,
                                      coerce=int)
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)

    def clean_product_id(self):
        product_id = self.cleaned_data['product_id']
        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise forms.ValidationError("Выбранный продукт не существует")
        return product_id