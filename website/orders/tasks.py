from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
import logging

from .models import Order

logger = logging.getLogger(__name__)

@shared_task
def order_created(order_id):
    """
    Задание по отправке уведомления по электронной почте
    при успешном создании заказа.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        # Обработка ошибки, если заказ не существует
        logger.error(force_str(_(f'Order with id {order_id} does not exist')))
        return False

    subject = force_str(_(f'Order number: {order.id}'))
    message = force_str(_(f'Dear {order.first_name},\n\n' \
               'You have successfully placed an order.' \
               f'Your order ID is {order.id}.'))
    recipient = [order.email]
    email_sent_successfully = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient)
    if not email_sent_successfully:
        # Обработка ошибки, если электронное письмо не было отправлено
        logger.error(force_str(_(f'Email was not sent to {recipient}')))
        return False
    
    return True