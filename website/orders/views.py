from django.shortcuts import render

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

    Args:
        request (HttpRequest): The HttpRequest for creating the Order.

    Returns:
        HttpResponse: The HttpReponse object that contains the rendered 
        OrderCreateForm template with the Cart and the form instance.
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
            return render(request,
                          'orders/order/created.html',
                          {'order': order})
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})
