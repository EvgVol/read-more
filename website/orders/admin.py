from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Inline class used to display information about items included in the order in the Django admin interface.
    Defines the model for the inline form and adds the ability to select products by ID instead of using a dropdown.

    Attributes:
        model: The model used for the inline form.
        raw_id_fields: Fields to display as IDs.

    """
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Class defining the Django admin interface for the `Order` model.
    Defines the fields to display in the list of orders, filters, and inline elements to display items included in the order.

    Attributes:
        list_display: The fields to display in the list of orders.
        list_filter: Filters to use in the list of orders.
        inlines: Inline elements to display items included in the order.

    """
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
