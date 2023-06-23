from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CouponsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coupons'
    verbose_name = _('coupons')
