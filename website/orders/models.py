from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shop.models import Product


class Order (models.Model):
    """Represents an order placed by a customer."""
    
    first_name = models.CharField(_("first name"), max_length=50,
                                  help_text=_("Enter your first name"))
    last_name = models.CharField(_("last name"), max_length=50,
                                 help_text=_("Enter your last name"))
    email = models.EmailField(_("email"),
                              help_text=_("Enter your email address"))
    address = models.CharField(_("address"), max_length=250,
                               help_text=_("Enter your shipping address"))
    postal_code = models.CharField(_("postal code"), max_length=50,
                                   help_text=_("Enter your postal code"))
    city = models.CharField(_("city"), max_length=100,
                            help_text=_("Enter your city"))
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)
    paid = models.BooleanField(_("paid"), default=False)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return _(f"Order {self.id}")

    @property
    def get_total_cost(self):
        """Calculates the total cost of the order."""
        return sum(item.get_cost() for item in self.items.all())

    def get_absolute_url(self):
        return reverse("orders:order_list", args=[self.id])


class OrderItem (models.Model):
    """
    Represents an item in an order that is linked to a corresponding product.
    """

    order = models.ForeignKey(Order,
                              verbose_name=_("order"),
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                verbose_name=_("product"),
                                on_delete=models.CASCADE)
    price = models.DecimalField(_("price"),
                                max_digits=10,
                                decimal_places=2)
    quantity = models.PositiveIntegerField(_("quantity"), default=1)

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return str(self.id)

    @property
    def get_cost(self):
        """Calculates the total cost of this item."""
        return self.price * self.quantity

    def get_absolute_url(self):
        return reverse("orders:order_detail", args=[self.id])
