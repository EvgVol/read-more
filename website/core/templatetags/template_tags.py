from django import template

from orders.models import Order


register = template.Library()


@register.filter(name='addclass')
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.inclusion_tag('core/dashboard/order-list.html')
def show_orders():
    orders = Order.objects.all()[:6]
    return {'orders': orders}