from django.shortcuts import get_object_or_404, redirect, render

from app.models import *
from cart.cart import *

from .forms import *


def order(request, coupon_code):
    cart = Cart(request)
    products_count = cart.__len__()
    products = cart.get_cart_products()
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    print("coupon_code", coupon_code)
    if Coupon.objects.filter(code=coupon_code).exists():
        coupon = Coupon.objects.get(code=coupon_code)
        if request.user not in coupon.users.all():
            coupon_percentage = coupon.percentage
            amount = cart.get_grand_total(coupon_percentage)
        else:
            amount = cart.get_total_price()
    else:
        amount = cart.get_total_price()
    billing_status = False
    quantity = cart.__len__()
    for product in products:
        product_id = product.id
        products = Product.objects.get(id=product_id)
    store = products.store
    order = Order.objects.create(
        user=user,
        store=store,
        billing_status=billing_status,
        amount=amount,
        quantity=quantity,
    )
    order.set_product(products)
    # cart.clear()
    return redirect("payment:initiate_payment", order.id)
