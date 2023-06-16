from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from actions.utils import create_action
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem


def order_create(request):
    """
    View function for creating a new order.

    If the request method is POST, this function validates the OrderCreateForm
    and saves a new Order and the OrderItem objects of the items from the cart
    for the authenticated user. Then clears the cart and shows a confirmation
    message.

    On GET request, it renders the OrderCreateForm with the Cart and returns 
    it as response.
    """
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # очистить корзину
            cart.clear()
            # create_action(request.user, _('Order has been made'))
            # messages.success(request,
            #                  _('Your order has been placed successfully'))
            return render(request,
                          'orders/invoice.html',
                          {'order': order})
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/checkout.html',
                  {'cart': cart, 'form': form})
