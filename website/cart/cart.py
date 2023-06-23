from decimal import Decimal
from django.conf import settings

from shop.models import Product
from coupons.models import Coupon


class Cart:
    """Корзина."""

    def __init__(self, request):
        """
        Инициализировать корзину.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # сохранить пустую корзину в сеансе
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # сохранить текущий примененный купон в сеансе
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        """
        Прокрутить товарные позиции корзины в цикле и
        получить товары из базы данных.
        """
        product_ids = self.cart.keys()
        # получить объекты product и добавить их в корзину
        products = Product.objects.filter(id__in=product_ids)\
                                  .prefetch_related('category')
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчитать все товарные позиции в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Добавить товар в корзину либо обновить его количество.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0, 'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def get_total_price(self):
        """
        Общая стоимость товаров в корзине.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    @property
    def get_total_quantity(self):
        """
        Общее количество товаров корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def get_unique_products(self):
        """
        Возвращает количество уникальных товаров в корзине.
        """
        product_ids = self.cart.keys()
        # получить объекты product и добавить их в корзину
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        unique_products = []
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            if item not in unique_products:
                unique_products.append(item)
        return len(unique_products)

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100) * self.get_total_price())
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

    def has_product(self, product):
        """
        Проверить наличие товара в корзине.
        """
        product_id = str(product.id)
        return product_id in self.cart

    def remove(self, product):
        """
        Удалить товар из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Очистить корзину.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()


    def save(self):
        # пометить сеанс как "измененный",
        # чтобы обеспечить его сохранение
        self.session.modified = True
