from django.shortcuts import render, get_object_or_404, redirect

from cart.forms import CartAddProductForm
from .models import Category, Product
from .forms import ProductForm, ProductImageFormSet


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


def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST,
                                      request.FILES,
                                      prefix='product_image_formset')

        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            return redirect('courses:product_detail',
                            {"category_slug": product.category.slug,
                             "product_slug": product.slug})
        else:
            print(form.errors, formset.errors)
    else:
        form = ProductForm()
        formset = ProductImageFormSet(prefix='product_image_formset')

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'shop/product/form.html', context)
