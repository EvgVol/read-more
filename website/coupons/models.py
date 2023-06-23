from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Coupon(models.Model):
    """
    Model representing a coupon that customers can use for discounts.
    """
    code = models.CharField(verbose_name=_('Code'),
                            max_length=50, unique=True)
    valid_from = models.DateTimeField(verbose_name=_('Valid from'),)
    valid_to = models.DateTimeField(verbose_name=_('Valid to'),)
    discount = models.IntegerField(
        verbose_name=_('Discount'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Percentage value (0 to 100)'))
    active = models.BooleanField(verbose_name=_('Active'))

    class Meta:
        verbose_name=_('coupon')
        verbose_name_plural=_('coupons')

    def __str__(self):
        return self.code
