from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    A form for creating a new order.

    ...
    
    Attributes
    ----------
    model : Order
        A model for creating new Order instance.
        
    Fields
    ------
    first_name : CharField
        A first name of the person placing an order.
    last_name : CharField
        A last name of the person placing an order.
    email : EmailField
        An email of the person placing an order.
    address : CharField
        A street address of the person placing an order.
    postal_code : CharField
        A postal code of the person placing an order.
    city : CharField
        A city where the person placing an order lives.
        
    Methods
    -------
    Meta:
        Fields of the form.
    """
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email',
                  'address', 'postal_code', 'city']
