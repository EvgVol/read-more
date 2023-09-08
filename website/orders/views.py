from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import gettext_lazy as _

from actions.utils import create_action
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem, Order
# from .tasks import order_created
from coupons.models import Coupon


def order_create(request):
    """View function for creating a new order."""
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # очищаем корзину
            cart.clear()

            if cart.coupon:
                messages.info(request,
                              (_('Your order has been placed successfully'
                                 'with the discount %(discount)s.') %
                              {'discount': f"{cart.coupon.discount}%"}))
            else:
                messages.success(request,
                                 _('Your order has been placed successfully'))
            return render(request,
                          'orders/invoice.html',
                          {'order': order})
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/checkout.html',
                  {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'orders/invoice.html',
                  {'order': order})
