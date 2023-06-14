from .cart import Cart


def cart(request):
    """Позволяет получать доступ к корзине из любого шаблона."""
    return {'cart': Cart(request)}
