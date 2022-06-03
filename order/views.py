from django.shortcuts import get_object_or_404, redirect, render
from .forms import *
from cart.cart import *
from app.models import *


def order(request, coupon_code):
    cart = Cart(request)
    orderform = orderform;
    if request.method == "POST":
        orderform = OrderForm(request.POST)
        if orderform.is_valid():
            products_count = cart.__len__()
            products = cart.get_cart_products()
            order = orderform.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.user = None
            order.store = store
            print('coupon_code', coupon_code)
            if Coupon.objects.filter(code=coupon_code).exists():
                coupon = Coupon.objects.get(code=coupon_code)
                if request.user not in coupon.users.all():
                    order.amount = cart.get_grand_total(coupon_percentage)
                else:
                    order.amount = cart.get_total_price()
            else:
                order.amount = cart.get_total_price()
            order.billing_status = False
            order.quantity = cart.__len__()
            for product in products:
                product_id = product.id
                products = Product.objects.get(id=product_id)                             
            order.save()
            order.set_product(products)                                       
            # cart.clear()
            return redirect("payment:initiate_payment", order.id)
        else:
            form_feedback = 'Order Invalid'
            return redirect("cart:cart_summary", slugified_store_name=slugified_store_name)
