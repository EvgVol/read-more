from django import template

from orders.models import Order


register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.inclusion_tag('orders/order-list.html')
def show_orders():
    orders = Order.objects.all()
    paid_orders = Order.objects.filter(paid=True)
    nopaid_orders = Order.objects.filter(paid=False)
    return {'orders': orders,
            'paid_orders': paid_orders,
            'nopaid_orders': nopaid_orders}