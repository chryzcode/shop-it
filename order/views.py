from venv import create
from django.shortcuts import get_object_or_404, redirect, render

from app.models import *
from cart.cart import *

from .forms import *


def order(request, coupon_code):
    cart = Cart(request)
    products = cart.get_cart_products()
    for product in products:
        product_id = product.id
        product = Product.objects.get(id=product_id)
    store = Store.objects.get(store_name=product.store)
    if not store.currency:
        error = "Store does'nt have a set currency for payment, drop a review for the store"
        return redirect('cart:cart_summary', store.slugified_store_name)
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
        )
        for product in products:
            product_id = product.id
            products = Product.objects.get(id=product_id)  
            order.set_product(products)
            products_qty = cart.get_cart_qty()
            print(products_qty)
            #pass products_qty data to the template of the url
            return redirect("payment:initiate_payment", order.id
            )
