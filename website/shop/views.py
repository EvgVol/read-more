from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType


from cart.forms import CartAddProductForm
from reviews.models import Review
from .models import Category, Product
from .forms import ProductForm
from reviews.forms import ReviewForm


def product_list(request, category_slug=None):
    """Выводит список товаров"""
    products = Product.objects.filter(available=True)
    cart_product_form = CartAddProductForm()
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)

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
    product_content_type = ContentType.objects.get_for_model(Product)
    comments = Review.objects.filter(content_type=product_content_type,
                                     object_id=product.pk)
    form = ReviewForm()

    return render(request,
                  'shop/product-detail.html',
                  {'product': product,
                   'comments': comments,
                   'form': form,
                   'product_content_type': product_content_type,
                   'cart_product_form': cart_product_form})


def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            form.instance = product
            form.save()
            return redirect('courses:product_detail', product.category.slug, product.slug)
    else:
        form = ProductForm()

    context = {
        'form': form,
    }
    return render(request, 'shop/product/form.html', context)
