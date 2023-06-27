from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views


app_name = 'cart'


urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path(_('add/<int:product_id>/'), views.cart_add, name='cart_add'),
    path(_('remove/<int:product_id>/'), views.cart_remove, name='cart_remove'),
    path(_('clear/'), views.cart_clear, name='cart_clear'),
    
]
