from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from account.models import *
from cart.cart import *
from order.models import *
from order.views import order
from payment.models import Payment

from .forms import *
from .models import *


def custom_error_404(request, exception):
    return render(request, "error-pages/404-page.html")


def custom_error_500(request):
    return render(request, "error-pages/500-page.html")


def home_page(request):
    return render(request, "base/index.html")


@login_required(login_url="/account/login/")
def a_store_all_products(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    all_products = Product.objects.filter(store=store)
    return render(
        request,
        "store/products.html",
        {"all_products": all_products, "store": store},
    )


@login_required(login_url="/account/login/")
def product_detail(request, slug):
    page = "product_detail"
    if request.user.is_authenticated:
        product = get_object_or_404(Product, slug=slug)
        if request.user.store_creator == True:
            store = Store.objects.get(store_name=request.user.store_name)
        else:
            store = Store.objects.get(
                store_name=store_staff.objects.get(user=request.user).store
            )
        category_product = Product.objects.filter(
            category=product.category, store=store
        ).exclude(id=product.id)[:6]
    else:
        product = get_object_or_404(Product, slug=slug)
        category_product = Product.objects.filter(
            category=product.category, store=store
        ).exclude(id=product.id)[:6]
    return render(
        request,
        "product/product-detail.html",
        {
            "product": product,
            "category_product": category_product,
            "store": store,
            "page": page,
        },
    )


@login_required(login_url="/account/login/")
def create_product(request):
    error = ""
    form = ProductForm
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    product_units = ProductUnit.objects.all()
    shipping_methods = ShippingMethod.objects.filter(store=store)
    categories = Category.objects.filter(created_by=store)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        product_name = request.POST.get("product_name")
        if Product.objects.filter(
            name=product_name, store=store, slug=slugify(product_name)
        ).exists():
            error = "Product already exists"
            return render(
                request,
                "store/create-product.html",
                {"form": form, "error": error, "product_units": product_units},
            )
        if form.is_valid():
            product = form.save(commit=False)
            product.store = Store.objects.get(store_name=store)
            product.created_by = store
            product.slug = slugify(product.name)
            if Product.objects.filter(slug=product.slug, created_by=store).exists():
                error = "Product already exists"
                return render(
                    request,
                    "store/create-product.html",
                    {
                        "form": form,
                        "error": error,
                        "product_units": product_units,
                        "categories": categories,
                    },
                )
            if not store.currency:
                error = "Please set your store currency in store settings"
                return render(
                    request,
                    "store/create-product.html",
                    {
                        "form": form,
                        "error": error,
                        "product_units": product_units,
                        "categories": categories,
                    },
                )
            if not shipping_methods:
                error = "Please set your store shipping methods"
                return render(
                    request,
                    "store/create-product.html",
                    {
                        "form": form,
                        "error": error,
                        "product_units": product_units,
                        "categories": categories,
                    },
                )
            product.currency = store.currency
            product.save()
            return redirect(
                "app:product_detail",
                slug=product.slug,
            )
    context = {"form": form, "categories": categories, "product_units": product_units}
    return render(request, "store/create-product.html", context)


@login_required(login_url="/account/login/")
def edit_product(request, slug):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    product = get_object_or_404(Product, slug=slug, created_by=store.id)
    form = ProductForm(instance=product)
    categories = Category.objects.filter(created_by=store.id)
    product_units = ProductUnit.objects.all()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = store.id
            product.save()
            return redirect(
                "app:product_detail",
                slug=product.slug,
            )
    context = {
        "form": form,
        "categories": categories,
        "product_units": product_units,
        "product": product,
    }
    return render(request, "store/create-product.html", context)


@login_required(login_url="/account/login/")
def delete_product(request, slug):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        product = get_object_or_404(Product, slug=slug, created_by=store.id)
        product.delete()
        return redirect("app:store_products")
    else:
        return redirect("app:store_products")


@login_required(login_url="/account/login/")
def store_admin(request):
    return render(request, "store/store-admin.html")


def store(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    products = Product.objects.filter(store=store).order_by("-created")
    return render(request, "store/store.html", {"store": store, "products": products})


@login_required(login_url="/account/login/")
def store_customers(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    customers = store.customers.all()
    return render(
        request, "store/store-customers.html", {"store": store, "customers": customers}
    )


@login_required(login_url="/account/login/")
def add_wishlist(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    product.wishlist.add(user)
    return redirect("app:wishlist")


@login_required(login_url="/account/login/")
def remove_wishlist(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    store = get_object_or_404(Store, store_name=product.store.store_name)
    product.wishlist.remove(user)
    return redirect("app:product_detail", slug=product.slug)


@login_required(login_url="/account/login/")
def wishlist(request):
    user = request.user
    wishlist = Product.objects.filter(wishlist=user)
    for product in wishlist:
        product_store = Store.objects.get(store_name=product.store.store_name)
    return render(
        request, "store/wishlist.html", {"wishlist": wishlist, "store": store}
    )


@login_required(login_url="/account/login/")
def add_category(request):
    form = CategoryForm
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            name = request.POST.get("name")
            if Category.objects.filter(name=name, created_by=store).exists():
                error = "Category already exists"
                return render(
                    request,
                    "store/create-category.html",
                    {"form": form, "error": error},
                )
            else:
                category = form.save(commit=False)
                store = Store.objects.get(store_name=store)
                category.created_by = store
                category.save()
                return redirect("app:all_category")
    context = {"form": form}
    return render(request, "store/create-category.html", context)


@login_required(login_url="/account/login/")
def edit_category(request, slug):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        category = get_object_or_404(Category, slug=slug, created_by=store)

    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
        category = get_object_or_404(Category, slug=slug, created_by=store)

    form = CategoryForm(instance=category)
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            if request.user.store_creator == True:
                category.created_by = store
            else:
                category.created_by = store_staff.objects.get(user=request.user).store
            category.save()
            return redirect("app:all_category")
    context = {
        "form": form,
    }
    return render(request, "store/create-category.html", context)


@login_required(login_url="/account/login/")
def delete_category(request, slug):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        category = get_object_or_404(Category, slug=slug, created_by=store)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
        category = get_object_or_404(Category, slug=slug, created_by=store)
    category.delete()
    return redirect("app:all_category")


@login_required(login_url="/account/login/")
def all_category(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        categories = Category.objects.filter(created_by=store)
        context = {"categories": categories}
        return render(request, "store/category.html", context)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
        categories = Category.objects.filter(created_by=store)
        context = {"categories": categories}
        return render(request, "store/category.html", context)


@login_required(login_url="/account/login/")
def a_store_all_categories(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    all_categories = Category.objects.filter(created_by=store.store_name)
    return render(
        request,
        "store/a-store-categories.html",
        {"all_categories": all_categories},
    )


@login_required(login_url="/account/login/")
def a_store_category_products(request, slugified_store_name, slug):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    category = get_object_or_404(Category, slug=slug, created_by=store)
    category_products = Product.objects.filter(
        category=category, store=store, in_stock=True
    )
    return render(
        request,
        "product/category-products.html",
        {"category_products": category_products, "category": category},
    )


@login_required(login_url="/account/login/")
def discount_products(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    products = Product.objects.filter(store=store, discount_percentage__gt=0)
    return render(
        request,
        "product/discount-products.html",
        {"products": products, "store": store},
    )


@login_required(login_url="/account/login/")
def create_coupon(request):
    if request.user.store_creator == False:
        error = "You are not authorized to create coupons"
        return render(request, "store/coupon.html", {"error": error})

    else:
        form = CouponForm
        if request.method == "POST":
            form = CouponForm(request.POST, request.FILES)
            if form.is_valid():
                code = request.POST.get("code")
                store = Store.objects.get(store_name=request.user.store_name)
                if Coupon.objects.filter(code=code, created_by=store).exists():
                    error = "Coupon already exists"
                    return render(
                        request,
                        "store/create-coupon.html",
                        {"form": form, "error": error},
                    )
                else:
                    coupon = form.save(commit=False)
                    store = Store.objects.get(store_name=request.user.store_name)
                    coupon.created_by = store
                    coupon.save()
                    return redirect("app:all_coupons")
        context = {"form": form}
        return render(request, "store/create-coupon.html", context)


@login_required(login_url="/account/login/")
def all_coupons(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        coupons = Coupon.objects.filter(created_by=store)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
        coupons = Coupon.objects.filter(created_by=store)
    for coupon in coupons:
        expiry_date = datetime.now().astimezone() - coupon.created_at
        expiry_date_seconds = expiry_date.total_seconds()
        minutes = expiry_date_seconds / 60
        if int(minutes) > coupon.expiry_date:
            coupon.delete()
    return render(
        request,
        "store/coupon.html",
        {"coupons": coupons},
    )


@login_required(login_url="/account/login/")
def delete_coupon(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        coupon = get_object_or_404(Coupon, pk=pk, created_by=store)
        coupon.delete()
        return redirect("app:all_coupons")
    else:
        return redirect("app:all_coupons")


@login_required(login_url="/account/login/")
def all_customers(request):
    if request.user.store_creator == True:
        store = request.user.store_name
    if request.user.store_staff == True:
        store = store_staff.objects.get(user=request.user).store

    customers = Store.objects.get(store_name=store).customers.all()
    return render(request, "store/customers.html", {"customers": customers})


@login_required(login_url="/account/login/")
def store_orders(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    if request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    orders = Order.objects.filter(store=store)
    if Payment.objects.filter(store=store.id, order__in=orders).exists():
        payment = Payment.objects.filter(store=store.id, order__in=orders)
    else:
        payment = None
    print(payment)
    return render(
        request, "store/store-order.html", {"orders": orders, "payment": payment}
    )


@login_required(login_url="/account/login/")
def store_order_detail(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    if request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    order = Order.objects.get(id=pk, store=store.id)
    order_items = OrderItem.objects.filter(order=order)
    if Payment.objects.filter(order=order, store=store.id).exists():
        payment = Payment.objects.get(order=order, store=store.id)
    else:
        payment = None
    return render(
        request,
        "store/store-order-detail.html",
        {"order": order, "payment": payment, "order_items": order_items},
    )
