from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from actions.utils import create_action
from .cart import Cart
from .forms import CartAddProductForm
from shop.models import Product


@require_POST
def cart_add(request, product_id):
    """Добавляет товар в корзину."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
        create_action(request.user, 'добавил в корзину', product)
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Удаляет товар из корзины."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    create_action(request.user, 'удалил из корзины', product)
    return redirect('cart:cart_detail')


@require_POST
def cart_clear(request):
    """Очищает корзину."""
    cart = Cart(request)
    cart.clear()
    create_action(request.user, 'очистил корзину')
    return redirect('cart:cart_detail')


def cart_detail(request):
    """Выводит страницу корзину с её содержимым."""
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True}
        )
    return render(request, 'cart/cart.html', {'cart': cart})