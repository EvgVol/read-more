from django import template

from orders.models import Order


register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.inclusion_tag('orders/order-list.html')
def show_orders():
    orders = Order.objects.all()
    
    return {'orders': orders}