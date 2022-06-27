from django.shortcuts import get_object_or_404, redirect, render

from app.models import *
from cart.cart import *

from .forms import *
from .models import *
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone


def order(request, coupon_code):
    cart = Cart(request)
    currency_symbol = cart.get_currency_symbol()
    currency_code = cart.get_currency_code()
    products = cart.get_cart_products()
    for product in products:
        product_id = product.id
        product = Product.objects.get(id=product_id)
    store = Store.objects.get(store_name=product.store)
    if not store.currency:
        error = (
            "Store does'nt have a set currency for payment, drop a review for the store"
        )
        return redirect("cart:cart_summary", store.slugified_store_name)
    else:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        if Coupon.objects.filter(code=coupon_code, created_by=store).exists():
            coupon = Coupon.objects.get(code=coupon_code, created_by=store)
            if request.user not in coupon.users.all():
                coupon.users.add(user)
                coupon_percentage = coupon.percentage
                amount = cart.get_grand_total(coupon_percentage)
            else:
                amount = cart.get_total_price()
        else:
            amount = cart.get_total_price()
        if Coupon.objects.filter(code=coupon_code, created_by=store).exists():
            coupon = True
        else:
            coupon = False
        billing_status = False
        quantity = cart.__len__()
        order = Order.objects.create(
            user=user,
            store=store,
            billing_status=billing_status,
            amount=amount,
            quantity=quantity,
            coupon=coupon,
            currency_symbol=currency_symbol,
            currency_code=currency_code,
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],
                price=item["price"],
            )
        return redirect("payment:initiate_payment", order.id)


def unpaid_order_mail_remainder(request):
    for order in Order.objects.filter(billing_status=False, mail_remainder=False):
        if order.user and order.date_created < timezone.now() - timedelta(days=20):
            store = Store.objects.get(store_name=order.store)
            current_site = get_current_site(request)
            path = f"payment/{order.id}"
            subject = f"You have unpaid order in {store.store_name} store on Shop!t"
            message = render_to_string(
                "payment/unpaid-order-email.html",
                {
                    "store": store,
                    "order": order,
                    "domain": current_site.domain+"/"+path,
                },
            )
            from_email = settings.EMAIL_HOST_USER
            to_email = [order.user.email]
            send_mail(subject, message, from_email, to_email)


