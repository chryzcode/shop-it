from django.shortcuts import get_object_or_404, render

from .models import Category, Product, User


# Create your views here.
def home_page(request):
    return render(request, "app/home.html")


def a_user_all_products(request, slugified_store_name):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    all_products = Product.objects.filter(created_by=user.id, in_stock=True)
    return render(
        request, "app/a-user-all-products.html", {"all_products": all_products}
    )


def a_user_all_categories(request, slugified_store_name):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    all_categories = Category.objects.filter(created_by=user.id)
    return render(
        request, "app/a-user-all-categories.html", {"all_categories": all_categories}
    )


def product_detail(request, slugified_store_name, slug):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    product = get_object_or_404(Product, slug=slug, created_by=user.id, in_stock=True)
    return render(request, "app/product-detail.html", {"product": product})


def a_user_category_products(request, slugified_store_name, slug):
    user = get_object_or_404(User, slugified_store_name=slugified_store_name)
    category = get_object_or_404(Category, slug=slug, created_by=user.id)
    category_products = Product.objects.filter(
        category=category, created_by=user.id, in_stock=True
    )
    return render(
        request,
        "app/category-products.html",
        {"category_products": category_products, "category": category},
    )
