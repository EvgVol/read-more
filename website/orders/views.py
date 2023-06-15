from django.shortcuts import render

from .models import Order


def orders_list(request):
    """Выводит список заказов."""
