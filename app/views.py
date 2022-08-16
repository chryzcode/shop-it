from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from notifications.models import Notification
from notifications.signals import notify

from account.context_processors import *
from account.models import *
from cart.cart import *
from customer.models import *
from order.models import *
from order.views import *
from payment.forms import *
from payment.models import *
from payment.models import Payment
from subscriptions.models import *
from subscriptions.views import *

from .forms import *
from .models import *


@login_required(login_url="account:login")
def mark_notification_read(request, id):
    if Notification.objects.filter(recipient=request.user, id=id).exists():
        notification = Notification.objects.get(recipient=request.user, id=id)
        notification.unread = False
        for key, values in notification.data.items():
            if "order" in key:
                order = Order.objects.get(id=values)
                notification.save()
                return redirect("app:store_order_detail", pk=order.id)
            if "payment" in key:
                order = Order.objects.get(id=values)
                payment = Payment.objects.get(order=order)
                notification.save()
                return redirect("app:store_order_detail", pk=payment.order.id)
            if "subscription" in key:
                subscription = Subscription.objects.get(id=values)
                notification.save()
                if subscription.duration.name == "monthly":
                    return redirect("app:monthly_subscription_plans")
                if subscription.duration.name == "yearly":
                    return redirect("app:yearly_subscription_plans")
            if "bank_details_url" in key:
                notification.save()
                return redirect(values)
            if "shipping_method_url" in key:
                notification.save()
                return redirect(values)
            if "currency_url" in key:
                notification.save()
                return redirect(values)
            if "product_detail_url" in key:
                notification.save()
                return redirect(values)
            if "customer_detail_url" in key:
                notification.save()
                return redirect(values)
            if "review_detail_url" in key:
                notification.save()
                return redirect(values)
            if "withdrawal_detail_url" in key:
                notification.save()
                return redirect(values)


@login_required(login_url="account:login")
def mark_all_notification_read(request):
    current_path = request.META.get("HTTP_REFERER")
    notifications = Notification.objects.filter(recipient=request.user, unread=True)
    for notification in notifications:
        notification.unread = False
        notification.save()
    return redirect(current_path)


def custom_error_404(request, exception):
    return render(request, "error-pages/404-page.html")


def custom_error_500(request):
    return render(request, "error-pages/500-page.html")


def home_page(request):
    domain = request.META["HTTP_HOST"]
    if domain == settings.DEFAULT_DOMAIN:
        if request.user.is_authenticated:
            subscription_check(request)
            subscription_check_mail_remainder(request)
            unpaid_order_mail_remainder(request)
    return render(request, "base/index.html")


@login_required(login_url="/account/login/")
def a_store_all_products(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    all_products = Product.objects.filter(store=store)
    all_products_count = all_products.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(all_products, 10)
    try:
        all_products = paginator.page(page)
    except PageNotAnInteger:
        all_products = paginator.page(1)
    except EmptyPage:
        all_products = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/products.html",
        {
            "all_products": all_products,
            "store": store,
            "all_products_count": all_products_count,
        },
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
                store_name=store_staff.objects.get(email=request.user.email).store
            )
        category_product = Product.objects.filter(
            category=product.category, store=store
        ).exclude(id=product.id)[:6]
    else:
        product = get_object_or_404(Product, slug=slug)
        category_product = Product.objects.filter(
            category=product.category, store=store
        ).exclude(id=product.id)[:6]
    reviews = Review.objects.filter(product=product, store=store)[:2]
    return render(
        request,
        "product/product-detail.html",
        {
            "product": product,
            "category_product": category_product,
            "store": store,
            "page": page,
            "reviews": reviews,
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
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    product_units = ProductUnit.objects.all()
    shipping_methods = Shipping_Method.objects.filter(store=store)
    bank_info = Bank_Info.objects.filter(store=store)
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
            if Product.objects.filter(slug=product.slug, store=store).exists():
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
            if not bank_info:
                error = "Please set your store bank info"
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
            staffs = store_staff.objects.filter(store=store)
            for staff in staffs:
                staff_user = User.objects.get(email=staff.email)
                notify.send(
                    store.owner,
                    recipient=staff_user,
                    verb=f"Added a new product {product.name}",
                    product_detail_url=product.get_absolute_url(),
                )
            notify.send(
                store.owner,
                recipient=store.owner,
                verb=f"Added a new product {product.name}",
                product_detail_url=product.get_absolute_url(),
            )
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
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    product = get_object_or_404(Product, slug=slug, store=store)
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
        product = get_object_or_404(Product, slug=slug, store=store)
        product.delete()
        return redirect("app:store_products")
    else:
        return redirect("app:store_products")


@login_required(login_url="/account/login/")
def store_admin(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    if Subscription_Timeline.objects.filter(store=store).exists():
        subscribed = True
        orders = Order.objects.filter(store=store, billing_status=True)
        last_24_orders = orders.filter(created__gt=timezone.now() - timedelta(hours=24))
        last_7_days_orders = orders.filter(
            created__gt=timezone.now() - timedelta(days=7)
        )

        product_dict = {}
        customer_dict = {}
        customers = Customer.objects.filter(store=store)
        last_24_customers = customers.filter(
            time__gt=timezone.now() - timedelta(hours=24)
        )
        the_last_7_days_customers = customers.filter(
            time__gt=timezone.now() - timedelta(days=7)
        )

        last_24_hours_total_customers = 0
        for last_24_customer in last_24_customers:
            last_24_hours_total_customers = last_24_hours_total_customers + 1
        if last_24_customers.count() > 0 and customers.count() > 0:
            last_24_customers_percentage = (
                last_24_customers.count() / customers.count() * 100
            )
        else:
            last_24_customers_percentage = 0

        today_total_amount = 0
        for last_24_order in last_24_orders:
            amount = last_24_order.amount
            today_total_amount = amount + today_total_amount
        if last_24_orders.count() > 0 and orders.count() > 0:
            last_24_orders_percentage = last_24_orders.count() / orders.count() * 100
        else:
            last_24_orders_percentage = 0

        last_7_days_total_amount = 0
        for order in last_7_days_orders:
            last_7_days_amount = order.amount
            last_7_days_total_amount = last_7_days_total_amount + last_7_days_amount
        if last_7_days_orders.count() > 0 and orders.count() > 0:
            last_7_days_orders_percentage = (
                last_7_days_orders.count() / orders.count() * 100
            )
        else:
            last_7_days_orders_percentage = 0

        last_7_days_total_customer = 0
        for last_7_days_customer in the_last_7_days_customers:
            last_7_days_total_customer = last_7_days_total_customer + 1
        if the_last_7_days_customers.count() > 0 and customers.count() > 0:
            last_7_days_customers_percentage = (
                the_last_7_days_customers.count() / customers.count() * 100
            )
        else:
            last_7_days_customers_percentage = 0

        last_1_month_orders = orders.filter(
            created__gt=timezone.now() - timedelta(days=30)
        )
        last_1_month_total_amount = 0
        for order in last_1_month_orders:
            last_1_month_amount = order.amount
            last_1_month_total_amount = last_1_month_total_amount + last_1_month_amount
        if last_1_month_orders.count() > 0 and orders.count() > 0:
            last_1_month_orders_percentage = (
                last_1_month_orders.count() / orders.count() * 100
            )
        else:
            last_1_month_orders_percentage = 0

        last_1_year_orders = orders.filter(
            created__gt=timezone.now() - timedelta(days=365)
        )
        last_1_year_total_amount = 0
        for order in last_1_year_orders:
            last_1_year_amount = order.amount
            last_1_year_total_amount = last_1_year_total_amount + last_1_year_amount
        if last_1_year_orders.count() > 0 and orders.count() > 0:
            last_1_year_orders_percentage = (
                last_1_year_orders.count() / orders.count() * 100
            )
        else:
            last_1_year_orders_percentage = 0

        last_1_year_customers = customers.filter(
            time__gt=timezone.now() - timedelta(days=365)
        )
        last_1_year_total_customer = 0
        for customer in last_1_year_customers:
            last_1_year_total_customer = last_1_year_total_customer + 1
        if last_1_year_customers.count() > 0 and customers.count() > 0:
            last_1_year_customers_percentage = (
                last_1_year_customers.count() / customers.count() * 100
            )
        else:
            last_1_year_customers_percentage = 0

        last_1_month_customers = customers.filter(
            time__gt=timezone.now() - timedelta(days=30)
        )
        last_1_month_total_customer = 0
        for customer in last_1_month_customers:
            last_1_month_total_customer = last_1_month_total_customer + 1
        if last_1_month_customers.count() > 0 and customers.count() > 0:
            last_1_month_customers_percentage = (
                last_1_month_customers.count() / customers.count() * 100
            )
        else:
            last_1_month_customers_percentage = 0

        for order in orders:
            if order.user:
                if User.objects.filter(email=order.user.email).exists():
                    user = User.objects.get(email=order.user.email)
                    if user in store.customers.all():
                        customer = Customer.objects.get(email=user.email)
                        customer_count = customer_count + 1
                        if customer in customer_dict:
                            customer_dict[customer] = (
                                customer_dict[customer] + customer_count
                            )
                        else:
                            customer_dict[customer] = customer_count
                    else:
                        customer = None
        customer_dict = (
            sorted(customer_dict.items(), key=lambda x: x[1], reverse=True)
        )[:5]

        orders = Order.objects.filter(store=store, billing_status=True)
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                product_name = Product.objects.get(
                    id=order_item.product.id, store=store
                )
                product_quantity = order_item.quantity
                if product_name in product_dict:
                    product_dict[product_name] = (
                        product_dict[product_name] + product_quantity
                    )
                else:
                    product_dict[product_name] = product_quantity
        product_dict = (
            sorted(product_dict.items(), key=lambda item: item[1], reverse=True)
        )[:5]
        latest_orders = Order.objects.filter(store=store).order_by("-created")[:5]
        latest_paid_orders = Order.objects.filter(
            store=store, billing_status=True
        ).order_by("-created")[:5]
        customers = store.customers.all()

        if Order.objects.filter(store=store).order_by("-created")[:1].exists():
            last_order = (
                Order.objects.filter(store=store).order_by("-created")[:1].first()
            )
            if store.currency.code != last_order.currency_code:
                today_total_amount = 0
                last_24_orders_percentage = 0
                last_7_days_total_amount = 0
                last_7_days_orders_percentage = 0
                last_1_month_amount = 0
                last_1_month_orders_percentage = 0
                last_1_year_total_amount = 0
                last_1_year_orders_percentage = 0

        if last_24_hours_sales.objects.filter(store=store).exists():
            if last_24_hours_sales.objects.filter(store=store).count() == 2:
                first_data = last_24_hours_sales.objects.filter(store=store).first()
                second_data = last_24_hours_sales.objects.filter(store=store).last()
                if second_data.percentage != last_24_orders_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_24_orders_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        last_24_hours_sales_total_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_24_hours_sales_total_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_24_hours_sales_total_growth = "shrinking"
                    else:
                        last_24_hours_sales_total_growth = "shrinking"
                else:
                    if last_24_orders_percentage > 0:
                        last_24_hours_sales_total_growth = "growth"
                    else:
                        last_24_hours_sales_total_growth = "shrinking"
            elif last_24_hours_sales.objects.filter(store=store).count() == 1:
                first_data = last_24_hours_sales.objects.filter(store=store).first()
                if first_data.percentage != last_24_orders_percentage:
                    second_data = last_24_hours_sales.objects.create(
                        store=store, percentage=last_24_orders_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        last_24_hours_sales_total_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_24_hours_sales_total_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_24_hours_sales_total_growth = "shrinking"
                    else:
                        last_24_hours_sales_total_growth = "shrinking"
                else:
                    if last_24_orders_percentage > 0:
                        last_24_hours_sales_total_growth = "growth"
                    else:
                        last_24_hours_sales_total_growth = "shrinking"
        else:
            last_24_hours_sales.objects.create(
                store=store, percentage=last_24_orders_percentage
            )
            if last_24_orders_percentage > 0:
                last_24_hours_sales_total_growth = "growth"
            else:
                last_24_hours_sales_total_growth = "shrinking"

        if last_7_days_sales.objects.filter(store=store).exists():
            if last_7_days_sales.objects.filter(store=store).count() == 2:
                first_data = last_7_days_sales.objects.filter(store=store).first()
                second_data = last_7_days_sales.objects.filter(store=store).last()
                if second_data.percentage != last_7_days_orders_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_7_days_orders_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        last_7_days_sales_total_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_7_days_sales_total_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_7_days_sales_total_growth = "shrinking"
                    else:
                        last_7_days_sales_total_growth = "shrinking"
                if last_7_days_orders_percentage > 0:
                    last_7_days_sales_total_growth = "growth"
                else:
                    last_7_days_sales_total_growth = "shrinking"
            elif last_7_days_sales.objects.filter(store=store).count() == 1:
                first_data = last_7_days_sales.objects.filter(store=store).first()
                if first_data.percentage != last_7_days_orders_percentage:
                    second_data = last_7_days_sales.objects.create(
                        store=store, percentage=last_7_days_orders_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        last_7_days_sales_total_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_7_days_sales_total_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_7_days_sales_total_growth = "shrinking"
                    else:
                        last_7_days_sales_total_growth = "shrinking"
                else:
                    if last_7_days_orders_percentage > 0:
                        last_7_days_sales_total_growth = "growth"
                    else:
                        last_7_days_sales_total_growth = "shrinking"
        else:
            last_7_days_sales.objects.create(
                store=store, percentage=last_7_days_orders_percentage
            )
            if last_7_days_orders_percentage > 0:
                last_7_days_sales_total_growth = "growth"
            else:
                last_7_days_sales_total_growth = "shrinking"

        if last_7_days_customers.objects.filter(store=store).exists():
            if last_7_days_customers.objects.filter(store=store).count() == 2:
                first_data = last_7_days_customers.objects.filter(store=store).first()
                second_data = last_7_days_customers.objects.filter(store=store).last()
                if second_data.percentage != last_7_days_customers_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_7_days_customers_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        last_7_days_customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_7_days_customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_7_days_customers_growth = "shrinking"
                    else:
                        last_7_days_customers_growth = "shrinking"
                if last_7_days_orders_percentage > 0:
                    last_7_days_customers_growth = "growth"
                else:
                    last_7_days_customers_growth = "shrinking"
            elif last_7_days_customers.objects.filter(store=store).count() == 1:
                first_data = last_7_days_customers.objects.filter(store=store).first()
                if first_data.percentage != last_7_days_orders_percentage:
                    second_data = last_7_days_customers.objects.create(
                        store=store, percentage=last_7_days_customers_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        last_7_days_customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_7_days_customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_7_days_customers_growth = "shrinking"
                    else:
                        last_7_days_customers_growth = "shrinking"
                else:
                    if last_7_days_orders_percentage > 0:
                        last_7_days_customers_growth = "growth"
                    else:
                        last_7_days_customers_growth = "shrinking"
        else:
            last_7_days_customers.objects.create(
                store=store, percentage=last_7_days_customers_percentage
            )
            if last_7_days_orders_percentage > 0:
                last_7_days_customers_growth = "growth"
            else:
                last_7_days_customers_growth = "shrinking"

        if last_24_hours_customers.objects.filter(store=store).exists():
            if last_24_hours_customers.objects.filter(store=store).count() == 2:
                first_data = last_24_hours_customers.objects.filter(store=store).first()
                second_data = last_24_hours_customers.objects.filter(store=store).last()
                if second_data.percentage != last_24_customers_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_24_customers_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        last_24_customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_24_customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_24_customers_growth = "shrinking"
                    else:
                        last_24_customers_growth = "shrinking"
                if last_24_customers_percentage > 0:
                    last_24_customers_growth = "growth"
                else:
                    last_24_customers_growth = "shrinking"
            elif last_24_hours_customers.objects.filter(store=store).count() == 1:
                first_data = last_24_hours_customers.objects.filter(store=store).first()
                if first_data.percentage != last_24_customers_percentage:
                    second_data = last_24_hours_customers.objects.create(
                        store=store, percentage=last_24_customers_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        last_24_customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_24_customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_24_customers_growth = "shrinking"
                    else:
                        last_24_customers_growth = "shrinking"
                else:
                    if last_24_customers_percentage > 0:
                        last_24_customers_growth = "growth"
                    else:
                        last_24_customers_growth = "shrinking"
        else:
            last_24_hours_customers.objects.create(
                store=store, percentage=last_24_customers_percentage
            )
            if last_24_customers_percentage > 0:
                last_24_customers_growth = "growth"
            else:
                last_24_customers_growth = "shrinking"

        if yearly_sales.objects.filter(store=store).exists():
            if yearly_sales.objects.filter(store=store).count() == 2:
                first_data = yearly_sales.objects.filter(store=store).first()
                second_data = yearly_sales.objects.filter(store=store).last()
                if second_data.percentage != last_1_year_orders_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_1_year_orders_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        yearly_sales_total_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        yearly_sales_total_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        yearly_sales_total_growth = "shrinking"
                    else:
                        yearly_sales_total_growth = "shrinking"
                if last_1_year_orders_percentage > 0:
                    yearly_sales_total_growth = "growth"
                else:
                    yearly_sales_total_growth = "shrinking"
            elif yearly_sales.objects.filter(store=store).count() == 1:
                first_data = yearly_sales.objects.filter(store=store).first()
                if first_data.percentage != last_24_customers_percentage:
                    second_data = yearly_sales.objects.create(
                        store=store, percentage=last_1_year_orders_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        yearly_sales_total_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        yearly_sales_total_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        yearly_sales_total_growth = "shrinking"
                    else:
                        yearly_sales_total_growth = "shrinking"
                else:
                    if last_1_year_orders_percentage > 0:
                        yearly_sales_total_growth = "growth"
                    else:
                        yearly_sales_total_growth = "shrinking"
        else:
            yearly_sales.objects.create(
                store=store, percentage=last_1_year_orders_percentage
            )
            if last_1_year_orders_percentage > 0:
                yearly_sales_total_growth = "growth"
            else:
                yearly_sales_total_growth = "shrinking"

        if last_30_days_sales.objects.filter(store=store).exists():
            if last_30_days_sales.objects.filter(store=store).count() == 2:
                first_data = last_30_days_sales.objects.filter(store=store).first()
                second_data = last_30_days_sales.objects.filter(store=store).last()
                if second_data.percentage != last_1_month_orders_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_1_month_orders_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        last_1_month_sales_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_1_month_sales_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_1_month_sales_growth = "shrinking"
                    else:
                        last_1_month_sales_growth = "shrinking"
                if last_1_month_orders_percentage > 0:
                    last_1_month_sales_growth = "growth"
                else:
                    last_1_month_sales_growth = "shrinking"
            elif last_30_days_sales.objects.filter(store=store).count() == 1:
                first_data = last_30_days_sales.objects.filter(store=store).first()
                if first_data.percentage != last_1_month_orders_percentage:
                    second_data = last_30_days_sales.objects.create(
                        store=store, percentage=last_1_month_orders_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        last_1_month_sales_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_1_month_sales_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_1_month_sales_growth = "shrinking"
                    else:
                        last_1_month_sales_growth = "shrinking"
                else:
                    if last_1_month_orders_percentage > 0:
                        last_1_month_sales_growth = "growth"
                    else:
                        last_1_month_sales_growth = "shrinking"
        else:
            last_30_days_sales.objects.create(
                store=store, percentage=last_1_month_orders_percentage
            )
            if last_1_month_orders_percentage > 0:
                last_1_month_sales_growth = "growth"
            else:
                last_1_month_sales_growth = "shrinking"

        if customers_yearly.objects.filter(store=store).exists():
            if customers_yearly.objects.filter(store=store).count() == 2:
                first_data = customers_yearly.objects.filter(store=store).first()
                second_data = customers_yearly.objects.filter(store=store).last()
                if second_data.percentage != last_1_year_customers_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_1_year_customers_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        customers_growth = "shrinking"
                    else:
                        customers_growth = "shrinking"
                if last_1_year_customers_percentage > 0:
                    customers_growth = "growth"
                else:
                    customers_growth = "shrinking"
            elif customers_yearly.objects.filter(store=store).count() == 1:
                first_data = customers_yearly.objects.filter(store=store).first()
                if first_data.percentage != last_1_year_customers_percentage:
                    second_data = customers_yearly.objects.create(
                        store=store, percentage=last_1_year_customers_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        customers_growth = "shrinking"
                    else:
                        customers_growth = "shrinking"
                else:
                    if last_1_year_customers_percentage > 0:
                        customers_growth = "growth"
                    else:
                        customers_growth = "shrinking"
        else:
            customers_yearly.objects.create(
                store=store, percentage=last_1_year_customers_percentage
            )
            if last_1_year_customers_percentage > 0:
                customers_growth = "growth"
            else:
                customers_growth = "shrinking"

        if customers_monthly.objects.filter(store=store).exists():
            if customers_monthly.objects.filter(store=store).count() == 2:
                first_data = customers_monthly.objects.filter(store=store).first()
                second_data = customers_monthly.objects.filter(store=store).last()
                if second_data.percentage != last_1_month_customers_percentage:
                    first_data.percentage = second_data.percentage
                    first_data.save()
                    second_data.percentage = last_1_month_customers_percentage
                    second_data.save()
                    if second_data.percentage > first_data.percentage:
                        last_30_customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_30_customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_30_customers_growth = "shrinking"
                    else:
                        last_30_customers_growth = "shrinking"
                if last_1_month_customers_percentage > 0:
                    last_30_customers_growth = "growth"
                else:
                    last_30_customers_growth = "shrinking"
            elif customers_monthly.objects.filter(store=store).count() == 1:
                first_data = customers_monthly.objects.filter(store=store).first()
                if first_data.percentage != last_1_month_customers_percentage:
                    second_data = customers_monthly.objects.create(
                        store=store, percentage=last_1_month_customers_percentage
                    )
                    if second_data.percentage > first_data.percentage:
                        last_30_customers_growth = "growth"
                    elif second_data.percentage == first_data.percentage:
                        last_30_customers_growth = "stagnant"
                    elif second_data.percentage < first_data.percentage:
                        last_30_customers_growth = "shrinking"
                    else:
                        last_30_customers_growth = "shrinking"
                else:
                    if last_1_month_customers_percentage > 0:
                        last_30_customers_growth = "growth"
                    else:
                        last_30_customers_growth = "shrinking"
        else:
            customers_monthly.objects.create(
                store=store, percentage=last_1_month_customers_percentage
            )
            if last_1_month_customers_percentage > 0:
                last_30_customers_growth = "growth"
            else:
                last_30_customers_growth = "shrinking"

        return render(
            request,
            "store/store-admin.html",
            {
                "customer_dict": customer_dict,
                "product_dict": product_dict,
                "today_total_amount": today_total_amount,
                "latest_paid_orders": latest_paid_orders,
                "latest_orders": latest_orders,
                "last_24_hours_total_customers": last_24_hours_total_customers,
                "customers": customers,
                "store": store,
                "subscribed": subscribed,
                "last_24_orders_percentage": int(last_24_orders_percentage),
                "last_24_customers_percentage": int(last_24_customers_percentage),
                "last_7_days_orders_percentage": int(last_7_days_orders_percentage),
                "last_7_days_total_amount": last_7_days_total_amount,
                "last_7_days_total_customer": last_7_days_total_customer,
                "last_7_days_customers_percentage": int(
                    last_7_days_customers_percentage
                ),
                "last_1_month_orders_percentage": int(last_1_month_orders_percentage),
                "last_1_month_total_amount": last_1_month_total_amount,
                "last_1_year_orders_percentage": int(last_1_year_orders_percentage),
                "last_1_year_total_amount": last_1_year_total_amount,
                "last_1_year_customers_percentage": int(
                    last_1_year_customers_percentage
                ),
                "last_1_year_total_customer": last_1_year_total_customer,
                "last_1_month_customers_percentage": int(
                    last_1_month_customers_percentage
                ),
                "last_1_month_total_customer": last_1_month_total_customer,
                "last_7_days_sales_total_growth": last_7_days_sales_total_growth,
                "last_24_hours_sales_total_growth": last_24_hours_sales_total_growth,
                "last_7_days_customers_growth": last_7_days_customers_growth,
                "last_24_customers_growth": last_24_customers_growth,
                "yearly_sales_total_growth": yearly_sales_total_growth,
                "last_1_month_sales_growth": last_1_month_sales_growth,
                "customers_growth": customers_growth,
                "last_30_customers_growth": last_30_customers_growth,
            },
        )
    else:
        subscribed = False
        messages.error(request, "You need to subscribe view this page.")
        return render(request, "store/store-admin.html", {"subscribed": subscribed})


def store(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    products = Product.objects.filter(store=store).order_by("-created")[:12]
    return render(
        request,
        "store/store.html",
        {
            "store": store,
            "products": products,
            "slugified_store_name": slugified_store_name,
        },
    )


@login_required(login_url="/account/login/")
def store_customers(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    customers = Customer.objects.filter(store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(customers, 10)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
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
    page = request.GET.get("page", 1)
    paginator = Paginator(wishlist, 10)
    try:
        wishlist = paginator.page(page)
    except PageNotAnInteger:
        wishlist = paginator.page(1)
    except EmptyPage:
        wishlist = paginator.page(paginator.num_pages)
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
            store_name=store_staff.objects.get(email=request.user.email).store
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
            store_name=store_staff.objects.get(email=request.user.email).store
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
            store_name=store_staff.objects.get(email=request.user.email).store
        )
        category = get_object_or_404(Category, slug=slug, created_by=store)
    category.delete()
    return redirect("app:all_category")


@login_required(login_url="/account/login/")
def all_category(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    categories = Category.objects.filter(created_by=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(categories, 10)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    return render(request, "store/category.html", {"categories": categories})


def store_category_products(request, slugified_store_name, slug):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    if Subscription_Timeline.objects.filter(store=store).exists():
        SEO = True
    else:
        SEO = False
    category = get_object_or_404(Category, slug=slug, created_by=store)
    get_store_category_products(request)
    products = Product.objects.filter(category=category, store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 20)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/view-more.html",
        {"products": products, "category": category, "store": store, "SEO": SEO},
    )


def all_store_products(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    if Subscription_Timeline.objects.filter(store=store).exists():
        SEO = True
    else:
        SEO = False
    products = Product.objects.filter(store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 20)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/view-more.html",
        {"products": products, "store": store, "SEO": SEO},
    )


@login_required(login_url="/account/login/")
def discount_products(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    products = Product.objects.filter(store=store, discount_percentage__gt=0)
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 10)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(
        request,
        "product/discount-products.html",
        {"products": products, "store": store},
    )


@login_required(login_url="/account/login/")
def create_coupon(request):
    form = CouponForm
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        if Subscription_Timeline.objects.filter(store=store).exists():
            store_coupons = Coupon.objects.filter(store=store)
            store_subscription = Subscription_Timeline.objects.get(store=store)
            if store_subscription.subscription.name == "Professional":
                store_coupon_limit = 10
            elif store_subscription.subscription.name == "Standard":
                store_coupon_limit = 3
            else:
                store_coupon_limit = 0
            if store_coupons.count() <= store_coupon_limit:
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
                            store = Store.objects.get(
                                store_name=request.user.store_name
                            )
                            coupon.created_by = store
                            coupon.save()
                            return redirect("app:all_coupons")
            else:
                messages.error(request, "You have reached the coupon limit")
    else:
        messages.error(request, "You are not authorized to create coupon")
    context = {"form": form}
    return render(request, "store/create-coupon.html", context)


@login_required(login_url="/account/login/")
def all_coupons(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
        coupons = Coupon.objects.filter(created_by=store)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
        coupons = Coupon.objects.filter(created_by=store)
    for coupon in coupons:
        expiry_date = datetime.now().astimezone() - coupon.created_at
        expiry_date_seconds = expiry_date.total_seconds()
        minutes = expiry_date_seconds / 60
        if int(minutes) > coupon.expiry_date:
            coupon.delete()
    page = request.GET.get("page", 1)
    paginator = Paginator(coupons, 10)
    try:
        coupons = paginator.page(page)
    except PageNotAnInteger:
        coupons = paginator.page(1)
    except EmptyPage:
        coupons = paginator.page(paginator.num_pages)
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
        store = Store.objects.get(store_name=request.user.store_name)
    if request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )

    customers = Customer.objects.filter(store=store)
    return render(request, "store/customers.html", {"customers": customers})


@login_required(login_url="/account/login/")
def store_orders(request):
    payment = None
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    if request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    orders = Order.objects.filter(store=store)
    orders_count = orders.count()
    if orders:
        for order in orders:
            if Payment.objects.filter(order=order).exists():
                payment = Payment.objects.get(order=order)
            else:
                payment = None
    page = request.GET.get("page", 1)
    paginator = Paginator(orders, 10)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/store-order.html",
        {"orders": orders, "payment": payment, "orders_count": orders_count},
    )


@login_required(login_url="/account/login/")
def unpaid_store_orders(request):
    payment = None
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    if request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    orders = Order.objects.filter(store=store, billing_status=False)
    orders_count = orders.count()
    if orders:
        for order in orders:
            if order.date_created < timezone.now() - timedelta(days=30):
                order.delete()
            if Payment.objects.filter(order=order).exists():
                payment = Payment.objects.get(order=order)
            else:
                payment = None
    page = request.GET.get("page", 1)
    paginator = Paginator(orders, 10)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/store-order.html",
        {"orders": orders, "payment": payment, "orders_count": orders_count},
    )


@login_required(login_url="/account/login/")
def store_order_detail(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    if request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
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


def store_review(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    if request.user.is_authenticated:
        form = AuthReviewForm
    else:
        form = nonAuthReviewForm
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.store = store
            if request.user.is_authenticated:
                review.email = request.user.email
                review.full_name = request.user.full_name
            review.save()
            staffs = store_staff.objects.filter(store=store)
            for staff in staffs:
                staff_user = User.objects.get(email=staff.email)
                notify.send(
                    store.owner,
                    recipient=staff_user,
                    verb=f"{store.store_name} just got a new store review",
                    review_detail_url=reverse(
                        "app:store_review_detail", kwargs={"pk": review.pk}
                    ),
                )
            notify.send(
                store.owner,
                recipient=store.owner,
                verb=f"{store.store_name} just got a new store review",
                review_detail_url=reverse(
                    "app:store_review_detail", kwargs={"pk": review.pk}
                ),
            )
            return redirect("app:store", slugified_store_name=slugified_store_name)
    context = {"form": form, "store": store}
    return render(request, "store/store-review.html", context)


@login_required(login_url="/account/login/")
def store_review_list(request):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    reviews = Review.objects.filter(store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(reviews, 10)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    return render(request, "store/store-review-list.html", {"reviews": reviews})


def product_store_review(request, slugified_store_name, slug):
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    product = Product.objects.get(slug=slug, store=store)
    if request.user.is_authenticated:
        form = authProductReviewForm
    else:
        form = nonAuthProductReviewForm
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.email = request.user.email
                review.full_name = request.user.full_name
            review.store = store
            review.save()
            staffs = store_staff.objects.filter(store=store)
            for staff in staffs:
                staff_user = User.objects.get(email=staff.email)
                notify.send(
                    store.owner,
                    recipient=staff_user,
                    verb=f"{store.store_name} just got a new product review",
                    review_detail_url=reverse(
                        "app:store_review_detail", kwargs={"pk": review.pk}
                    ),
                )
            notify.send(
                store.owner,
                recipient=store.owner,
                verb=f"{store.store_name} just got a new product review",
                review_detail_url=reverse(
                    "app:store_review_detail", kwargs={"pk": review.pk}
                ),
            )
            return redirect(
                "customer:customer_product_detail",
                slugified_store_name=slugified_store_name,
                slug=slug,
            )
    context = {"form": form, "store": store}
    return render(request, "store/store-review.html", context)


@login_required(login_url="/account/login/")
def store_review_detail(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    elif request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    review = Review.objects.get(id=pk, store=store)
    if User.objects.filter(email=review.email).exists():
        user = User.objects.get(email=review.email)
        if user in store.customers.all():
            customer = Customer.objects.get(email=review.email)
        else:
            customer = None
    else:
        customer = None
    return render(
        request,
        "store/store-review-detail.html",
        {"review": review, "customer": customer},
    )


@login_required(login_url="/account/login/")
def yearly_subscription_plans(request):
    reccuring_sub = None
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    duration = Duration.objects.get(name="yearly")
    plans = Subscription.objects.filter(duration=duration)
    if RecurringSubscriptionData.objects.filter(user=request.user).exists():
        reccuring_sub_data = RecurringSubscriptionData.objects.get(user=request.user)
        if reccuring_sub_data.charge == True:
            reccuring_sub = True
        else:
            reccuring_sub = False
    return render(
        request,
        "store/subscription-plans.html",
        {"plans": plans, "store": store, "reccuring_sub": reccuring_sub},
    )


@login_required(login_url="/account/login/")
def monthly_subscription_plans(request):
    reccuring_sub = None
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    duration = Duration.objects.get(name="monthly")
    plans = Subscription.objects.filter(duration=duration)
    if RecurringSubscriptionData.objects.filter(user=request.user).exists():
        reccuring_sub_data = RecurringSubscriptionData.objects.get(user=request.user)
        if reccuring_sub_data.charge == True:
            reccuring_sub = True
        else:
            reccuring_sub = False
    return render(
        request,
        "store/subscription-plans.html",
        {"plans": plans, "store": store, "reccuring_sub": reccuring_sub},
    )


@login_required(login_url="/account/login/")
def transanction_history(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    payments = Payment.objects.filter(store=store)
    customers = store.customers.all()
    page = request.GET.get("page", 1)
    paginator = Paginator(payments, 10)
    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/transanction-history.html",
        {"payments": payments, "store": store, "customers": customers},
    )


@login_required(login_url="/account/login/")
def store_staff_page(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    store_staffs = store_staff.objects.filter(store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(store_staffs, 10)
    try:
        store_staffs = paginator.page(page)
    except PageNotAnInteger:
        store_staffs = paginator.page(1)
    except EmptyPage:
        store_staffs = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/store-staff-page.html",
        {"store_staffs": store_staffs, "store": store},
    )


@login_required(login_url="/account/login/")
def shipping_method_list(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    shipping_methods = Shipping_Method.objects.filter(store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(shipping_methods, 10)
    try:
        shipping_methods = paginator.page(page)
    except PageNotAnInteger:
        shipping_methods = paginator.page(1)
    except EmptyPage:
        shipping_methods = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/all-shipping-method.html",
        {"shipping_methods": shipping_methods, "store": store},
    )


@login_required(login_url="/account/login/")
def add_shipping_method(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        form = ShippingMethodForm
        if request.method == "POST":
            form = ShippingMethodForm(request.POST)
            if form.is_valid():
                location = form.cleaned_data["location"]
                shipping_method = form.save(commit=False)
                shipping_method.store = store
                if Shipping_Method.objects.filter(
                    location=location, store=store
                ).exists():
                    error = "Shipping Method already exists"
                    return render(
                        request,
                        "store/shipping-method.html",
                        {"form": form, "error": error},
                    )
                if not store.currency:
                    error = "Please select a currency in your store settings"
                    return render(
                        request,
                        "store/shipping-method.html",
                        {"form": form, "error": error},
                    )
                shipping_method.save()
                return redirect("app:shipping_method_list")
        return render(request, "store/shipping-method.html", {"form": form})
    else:
        error = "You are not authorized"
        return render(
            request, "store/shipping-method.html", {"error": error, "form": form}
        )


@login_required(login_url="/account/login/")
def edit_shipping_method(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        shipping_method = get_object_or_404(Shipping_Method, pk=pk)
        form = ShippingMethodForm(instance=shipping_method)
        if request.method == "POST":
            form = ShippingMethodForm(request.POST, instance=shipping_method)
            if form.is_valid():
                shipping_method = form.save(commit=False)
                shipping_method.store = store
                if Shipping_Method.objects.filter(
                    location=shipping_method.location, store=store
                ).exists():
                    error = "Shipping Method already exists"
                    return render(
                        request,
                        "store/shipping-method.html",
                        {"form": form, "error": error},
                    )
                shipping_method.save()
                return redirect("app:shipping_method_list")
        return render(request, "store/shipping-method.html", {"form": form})
    else:
        error = "You are not authorized"
        return render(
            request, "store/shipping-method.html", {"error": error, "form": form}
        )


@login_required(login_url="/account/login/")
def delete_shipping_method(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        shipping_method = get_object_or_404(Shipping_Method, pk=pk)
        if shipping_method:
            shipping_method.delete()
            return redirect("app:shipping_method_list")
    else:
        error = "You are not authorized"
        return render(request, "store/shipping-method.html", {"error": error})


@login_required(login_url="/account/login/")
def store_customers_details(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    elif request.user.store_staff == True:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    customer = get_object_or_404(Customer, pk=pk)
    customer_user = User.objects.get(email=customer.email)
    reviews = Review.objects.filter(email=customer_user.email, store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(reviews, 5)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    orders = Order.objects.filter(user=customer_user, store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(orders, 5)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    return render(
        request,
        "store/customer-details.html",
        {
            "customer": customer,
            "store": store,
            "reviews": reviews,
            "orders": orders,
            "customer_user": customer_user,
        },
    )


def product_review_list(request, slugified_store_name, slug):
    store = Store.objects.get(slugified_store_name=slugified_store_name)
    product = Product.objects.get(slug=slug, store=store)
    reviews = Review.objects.filter(product=product)
    page = request.GET.get("page", 1)
    paginator = Paginator(reviews, 10)
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    return render(
        request,
        "customer/product-review-list.html",
        {"reviews": reviews, "product": product, "store": store},
    )


def store_wallet(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    wallets = Wallet.objects.filter(store=store)
    naira_wallet = None
    usd_wallet = None
    usd_currency_code = "USD"
    naira_currency_code = "NGN"
    form = WalletForm
    if wallets:
        if Currency.objects.filter(code="NGN").exists():
            naira_currency = Currency.objects.get(code="NGN")
            if Wallet.objects.filter(store=store, currency=naira_currency).exists():
                naira_wallet = Wallet.objects.get(store=store, currency=naira_currency)
        if Currency.objects.filter(code="USD").exists():
            usd_currency = Currency.objects.get(code="USD")
            if Wallet.objects.filter(store=store, currency=usd_currency).exists():
                usd_wallet = Wallet.objects.get(store=store, currency=usd_currency)

    wallet_transanctions = Wallet_Transanction.objects.filter(store=store)
    page = request.GET.get("page", 1)
    paginator = Paginator(wallet_transanctions, 5)
    try:
        wallet_transanctions = paginator.page(page)
    except PageNotAnInteger:
        wallet_transanctions = paginator.page(1)
    except EmptyPage:
        wallet_transanctions = paginator.page(paginator.num_pages)

    withdrawal_transanctions = Withdrawal_Transanction.objects.filter(store=store)
    withdrawal_page = request.GET.get("withdrawal_page", 1)
    withdrawal_paginator = Paginator(withdrawal_transanctions, 5)
    try:
        withdrawal_transanctions = withdrawal_paginator.page(withdrawal_page)
    except PageNotAnInteger:
        withdrawal_transanctions = withdrawal_paginator.page(1)
    except EmptyPage:
        withdrawal_transanctions = withdrawal_paginator.page(
            withdrawal_paginator.num_pages
        )

    return render(
        request,
        "store/wallet.html",
        {
            "wallets": wallets,
            "store": store,
            "naira_wallet": naira_wallet,
            "usd_wallet": usd_wallet,
            "usd_currency_code": usd_currency_code,
            "naira_currency_code": naira_currency_code,
            "wallet_transanctions": wallet_transanctions,
            "withdrawal_transanctions": withdrawal_transanctions,
            "form": form,
        },
    )


def company_review(request):
    if request.user.is_authenticated:
        form = CompanyAuthReviewForm
    else:
        form = CompanyNonAuthReviewForm
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                from_email = request.user.email
            else:
                from_email = form.cleaned_data["email"]
            to_email = settings.EMAIL_HOST_USER
            subject = "Shopit Review from " + from_email
            message = form.cleaned_data["review"]
            send_mail(subject, message, from_email, [to_email])
            return redirect("/")
    return render(request, "company-review.html", {"form": form})


def company_team(request):
    return render(request, "company-team.html")


def get_state(request, iso2):
    url = f"https://api.countrystatecity.in/v1/countries/{iso2}/states"

    headers = {"X-CSCAPI-KEY": settings.COUNTRY_STATE_CITY_API_KEY}
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    states = {}
    for state in data:
        states[state["name"]] = state["iso2"]
    states = sorted(states.items(), key=lambda x: x[0])
    response = JsonResponse({"states": states})
    return response


@login_required(login_url="/account/login/")
def notification_page(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    user = User.objects.get(email=request.user.email)
    return render(request, "store/notifications.html", {"store": store, "user": user})


def newsletter_page(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
   
    if Store_Newsletter.objects.filter(store=store).exists():
        store_newsletter = Store_Newsletter.objects.get(store=store)
        subscribers = store_newsletter.customers.all()
        newsletters = Newsletter.objects.filter(store=store_newsletter)
        page = request.GET.get("page", 1)
        paginator = Paginator(newsletters, 5)
        try:
            newsletters = paginator.page(page)
        except PageNotAnInteger:
            newsletters = paginator.page(1)
        except EmptyPage:
            newsletters = paginator.page(paginator.num_pages)
        form = NewsletterForm()
        if request.method == "POST":
            form = NewsletterForm(request.POST)
            if form.is_valid():
                newsletter = form.save(commit=False)
                newsletter.store = store_newsletter
                newsletter.save()
                return redirect("app:newsletter_page")
    else:
        newsletters = None
        store_newsletter = None
        form = None
        subscribers = None
    return render(request, "store/all-newsletter-page.html", {"store": store,  'form': form, "newsletters": newsletters, "store_newsletter": store_newsletter, "subscribers": subscribers})



@login_required(login_url="/account/login/")
def generate_store_newsletter(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        if Store_Newsletter.objects.filter(store=store).exists():
            messages.error(request, "You have already generated a newsletter")
            return redirect("app:newsletter_page")
        else:
            Store_Newsletter.objects.create(
            store=store,
        )
        return redirect("app:newsletter_page")
    else:
        messages.error(request, "You are not authorized")
        return redirect("app:newsletter_page")


@login_required(login_url="/account/login/")
def draft_newsletter(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    if Store_Newsletter.objects.filter(store=store).exists():
        store_newsletter = Store_Newsletter.objects.get(store=store)
        newsletters = Newsletter.objects.filter(store=store_newsletter)
        form = NewsletterForm(request.POST or None)
        if request.method == "POST":
            title = request.POST.get("title")
            body = request.POST.get("body")
            if form.is_valid():
                newsletter = form.save(commit=False)
                newsletter.store = store_newsletter
                newsletter.save()
                return redirect("app:newsletter_page")
            else:
                if form.errors:
                    messages.error(request, form.errors)
                    return redirect("app:newsletter_page")
    else:
        messages.error(request, "You have not generated a newsletter")
        return redirect("app:newsletter_page")
    return redirect("app:newsletter_page")

@login_required(login_url="/account/login/")
def edit_draft_newsletter(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    if Store_Newsletter.objects.filter(store=store).exists():
        store_newsletter = Store_Newsletter.objects.get(store=store)
        newsletter = Newsletter.objects.get(pk=pk, store=store_newsletter)
        form = NewsletterForm(request.POST or None, instance=newsletter)
        subscribers = store_newsletter.customers.all()
        if request.method == "POST":
            title = request.POST.get("title")
            body = request.POST.get("body")
            if form.is_valid():
                newsletter = form.save(commit=False)
                newsletter.store = store_newsletter
                newsletter.save()
                return redirect("app:newsletter_page")
            else:
                if form.errors:
                    messages.error(request, form.errors)
                    return redirect("app:newsletter_page")
    else:
        messages.error(request, "You have not generated a newsletter")
        return redirect("app:newsletter_page")
    return render(request, "store/all-newsletter-page.html", {"store": store, "newsletter": newsletter, "form": form, "subscribers": subscribers})


@login_required(login_url="/account/login/")
def publish_newsletter(request):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    form = NewsletterForm(request.POST or None)
    if Store_Newsletter.objects.filter(store=store).exists():
        store_newsletter = Store_Newsletter.objects.get(store=store)
        customer_list = []
        if request.method == "POST":
            if form.is_valid():
                subject = form.cleaned_data["title"]
                message = form.cleaned_data["body"]
                customers =  store_newsletter.customers.all()
                if customers:
                    for customer in customers:
                        customer_list.append(customer.email)
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [customer_list])
                    return redirect("app:newsletter_page")
                else:
                    messages.error(request, "You have not added any subscribed customers")
                    return redirect("app:newsletter_page")
                
            else:
                if form.errors:
                    messages.error(request, form.errors)
                    return redirect("app:newsletter_page")
    else:
        messages.error(request, "You have not generated a newsletter")
        return redirect("app:newsletter_page")


@login_required(login_url="/account/login/")
def delete_draft_newsletter(request, pk):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(email=request.user.email).store
        )
    if Store_Newsletter.objects.filter(store=store).exists():
        store_newsletter = Store_Newsletter.objects.get(store=store)
        newsletter = get_object_or_404(Newsletter, pk=pk, store=store_newsletter)
        newsletter.delete()
        return redirect("app:newsletter_page")
    else:
        messages.error(request, "You have not generated a newsletter")
        return redirect("app:newsletter_page")
                
            