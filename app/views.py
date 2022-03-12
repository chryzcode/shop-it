from django.shortcuts import get_object_or_404, redirect, render

from .forms import *
from .models import *

# Create your views here.


def custom_error_404(request, exception):
    return render(request, "error-pages/404-page.html")


def custom_error_500(request):
    return render(request, "error-pages/404-page.html")


def home_page(request):
    return render(request, "app/home.html")


def a_user_all_products(request, slugified_store_name):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    all_products = Product.objects.filter(created_by=user.id, in_stock=True)
    return render(
        request,
        "app/product-templates/a-user-all-products.html",
        {"all_products": all_products},
    )


def a_user_all_categories(request, slugified_store_name):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    all_categories = Category.objects.filter(created_by=user.id)
    return render(
        request,
        "app/product-templates/a-user-all-categories.html",
        {"all_categories": all_categories},
    )


def product_detail(request, slug, slugified_store_name):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    product = get_object_or_404(Product, slug=slug)
    category_product = Product.objects.filter(
        category=product.category, created_by=user.id
    ).exclude(id=product.id)[:6]
    return render(
        request,
        "app/product-templates/product-detail.html",
        {"product": product, "category_product": category_product},
    )


def a_user_category_products(request, slugified_store_name, slug):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    category = get_object_or_404(Category, slug=slug, created_by=user.id)
    category_products = Product.objects.filter(
        category=category, created_by=user.id, in_stock=True
    )
    return render(
        request,
        "app/product-templates/category-products.html",
        {"category_products": category_products, "category": category},
    )


def create_product(request):
    form = ProductForm
    categories = Category.objects.filter(created_by=request.user.id)
    product_units = ProductUnit.objects.all()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            return redirect(
                "app:product_detail",
                slug=product.slug,
                slugified_store_name=product.created_by.slugified_store_name,
            )
    context = {"form": form, "categories": categories, "product_units": product_units}
    return render(request, "app/product-templates/create-product.html", context)
