from datetime import datetime, timedelta
from decimal import Decimal
from locale import currency

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.forms import UseCouponForm
from app.models import *

from .cart import *


def cart_summary(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    coupon_code = "nil"
    grand_total = ""
    form_feedback = ""
    cart = Cart(request)
    if cart.get_store_name():
        cart_store_name = cart.get_store_name()
        cart_store = get_object_or_404(
            Store, slugified_store_name=slugify(cart_store_name)
        )
    else:
        cart_store_name = store.store_name
        cart_store = store
    cart_check = cart.store_check()
    form = UseCouponForm
    expired_coupons = Coupon.objects.all()
    for coupon in expired_coupons:
        expiry_date = datetime.now().astimezone() - coupon.created_at
        expiry_date_seconds = expiry_date.total_seconds()
        minutes = expiry_date_seconds / 60
        if int(minutes) > coupon.expiry_date:
            coupon.delete()
    if store.currency:
        store_currency_symbol = store.currency.symbol
    else:
        error = (
            "Store does'nt have a set currency for payment, drop a review for the store"
        )
        return render(
            request,
            "cart/cart-summary.html",
            {
                "cart": cart,
                "form": form,
                "grand_total": grand_total,
                "form_feedback": form_feedback,
                "store": store,
                "error": error,
                "cart_check": cart_check,
                "coupon_code": coupon_code,
            },
        )
    if request.method == "POST":
        form = UseCouponForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                coupon_code = form.cleaned_data.get("code")
                if coupon_code:
                    if Coupon.objects.filter(code=coupon_code).exists():
                        coupon = Coupon.objects.get(code=coupon_code)
                        if coupon.created_by == store:
                            if request.user not in coupon.users.all():
                                expiry_date = (
                                    datetime.now().astimezone() - coupon.created_at
                                )
                                expiry_date_seconds = expiry_date.total_seconds()
                                minutes = expiry_date_seconds / 60
                                if int(minutes) > coupon.expiry_date:
                                    form_feedback = "Copoun is Expired"
                                    coupon.delete()
                                else:
                                    coupon_percentage = coupon.percentage
                                    cart.get_grand_total(coupon_percentage)
                                    grand_total = int(
                                        cart.get_grand_total(coupon_percentage)
                                    )
                                    form = UseCouponForm
                                    form_feedback = "Coupon Successfully Used"

                            else:
                                form = UseCouponForm
                                form_feedback = "Copoun has been used by you"
                        else:
                            form = UseCouponForm
                            form_feedback = "Copoun is not valid for this product"
                    else:
                        form = UseCouponForm
                        form_feedback = "Coupon does not exist"
            else:
                form = UseCouponForm
                form_feedback = "You need to be authenticated to use coupon"
    return render(
        request,
        "cart/cart-summary.html",
        {
            "cart": cart,
            "form": form,
            "grand_total": grand_total,
            "form_feedback": form_feedback,
            "store": store,
            "store_currency_symbol": store_currency_symbol,
            "cart_check": cart_check,
            "coupon_code": coupon_code,
            "cart_store": cart_store,
        },
    )


def add_to_cart(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, qty=product_qty)
        if cart.store_check():
            product_qty = cart.__len__()
            response = JsonResponse({"qty": product_qty})
            return response
        else:
            cart.delete(product=product_id)
            product_qty = cart.__len__()
            response = JsonResponse({"qty": product_qty})
            return response


def delete_from_cart(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        cart.delete(product=product_id)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()
        response = JsonResponse({"qty": cartqty, "subtotal": int(carttotal)})
        return response


def update_cart(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        item_qty = int(request.POST.get("productqty"))
        product = Product.objects.get(id=product_id)
        if product.discount_percentage:
            price = product.price - (product.price * product.discount_percentage / 100)
        else:
            price = Product.objects.get(id=product_id).price
        cart.update(product=product_id, qty=product_qty, cartitemqty=item_qty, price=price)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()
        a_product_price = get_object_or_404(Product, id=product_id).price
        a_discount_price = get_object_or_404(Product, id=product_id).discount_price()

        if Product.objects.get(id=product_id).discount_price() < a_product_price:
            cartproductqty = item_qty * a_discount_price
        else:
            cartproductqty = item_qty * Decimal(a_product_price)
        currency = cart.get_currency_symbol()
        response = JsonResponse(
            {
                "qty": cartqty,
                "subtotal": f"{carttotal:,}",
                "cartproqty": (f"{cartproductqty:,}"),
                "currency": currency,
                "price":f"{int(price):,}",
            }
        )
        return response


def clear_all_cart(request, slugified_store_name):
    store = get_object_or_404(Store, slugified_store_name=slugified_store_name)
    cart = Cart(request)
    cart.clear()
    cartqty = cart.__len__()
    carttotal = cart.get_total_price()
    response = JsonResponse({"qty": cartqty, "subtotal": carttotal})
    return redirect("cart:cart_summary", slugified_store_name=slugified_store_name)
