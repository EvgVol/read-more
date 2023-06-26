from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from shop.models import Product
from coupons.models import Coupon


class Order (models.Model):
    """Represents an order placed by a customer."""
    
    first_name = models.CharField(verbose_name=_("first name"),
                                  max_length=50,
                                  help_text=_("Enter your first name"))
    last_name = models.CharField(verbose_name=_("last name"), max_length=50,
                                 help_text=_("Enter your last name"))
    email = models.EmailField(verbose_name=_("email"),
                              help_text=_("Enter your email address"))
    address = models.CharField(verbose_name=_("address"), max_length=250,
                               help_text=_("Enter your shipping address"))
    postal_code = models.CharField(verbose_name=_("postal code"),
                                   max_length=50,
                                   help_text=_("Enter your postal code"))
    city = models.CharField(verbose_name=_("city"), max_length=100,
                            help_text=_("Enter your city"))
    created = models.DateTimeField(verbose_name=_("created"),
                                   auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("updated"),
                                   auto_now=True)
    paid = models.BooleanField(verbose_name=_("paid"), default=False)
    coupon = models.ForeignKey(Coupon,
                               verbose_name=_("coupon"),
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    discount = models.IntegerField(_("discount"), default=0, 
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return force_str(_(f"Order {self.id}"))

    def get_total_cost_before_discount(self):
        return sum(item.get_cost for item in self.orderitem_set.all())

    def get_discount(self):
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        """Calculates the total cost of the order."""
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def get_items(self):
        """Gets all items related to this order."""
        return self.orderitem_set.all()

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_absolute_url(self):
        return reverse("orders:admin_order_detail", args=[self.id])


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
