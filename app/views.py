from django.shortcuts import render, get_object_or_404
from .models import Product, User, Category


# Create your views here.


def a_user_all_products(request, slugified_username):
    user = get_object_or_404(User, slugified_username=slugified_username)
    all_products = Product.objects.filter(created_by=user.id)
    return render(request, "app/all-products.html", {"all_products": all_products})


def a_user_all_categories(request, slugified_username):
    user = get_object_or_404(User, slugified_username=slugified_username)
    all_categories = Category.objects.filter(created_by=user.id)
    return render(
        request, "app/all-categories.html", {"all_categories": all_categories}
    )


def product_detail(request, slugified_username, slug):
    user = get_object_or_404(User, slugified_username=slugified_username)
    product = get_object_or_404(Product, slug=slug, created_by=user.id, in_stock=True)
    return render(request, "app/product-details.html", {"product": product})


def a_user_category_products(request, slugified_username, slug):
    user = get_object_or_404(User, slugified_username=slugified_username)
    category = get_object_or_404(Category, slug=slug, created_by=user.id)
    category_products = Product.objects.filter(
        category=category, created_by=user.id, in_stock=True
    )
    return render(
        request,
        "app/category-products.html",
        {"category_products": category_products, "category": category},
    )
