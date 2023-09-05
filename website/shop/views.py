from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from cart.forms import CartAddProductForm
from .models import Category, Product


def product_list(request):
    """Выводит список товаров"""
    products = Product.objects.filter(available=True)
    cart_product_form = CartAddProductForm()

    return render(request,
                  'shop/shop.html',
                  {'products': products,
                   'cart_product_form': cart_product_form})


def product_detail(request, category_slug, product_slug):
    """Выводит отдельный товар"""
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product,
                                category=category,
                                slug=product_slug,
                                available=True)
    cart_product_form = CartAddProductForm()

    return render(request,
                  'shop/product-detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})
