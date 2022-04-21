from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.models import *

from .cart import *
from app.forms import UseCouponForm
from datetime import datetime, timedelta

from .cart import * 


# Create your views here.
def cart_summary(request):
    cart = Cart(request)
    form = UseCouponForm
    if request.method == "POST":
        form = UseCouponForm(request.POST)
        if form.is_valid():
            coupon_code = form.cleaned_data.get("coupon_code")
            if Coupon.objects.filter(code=coupon_code).exists():
                coupon = Coupon.objects.get(code=coupon_code)
                if request.user in coupon.users.all():
                    if coupon.expiry_date == coupon.created_at + timedelta(minutes=coupon.expiry_date):
                        if coupon.active_coupon().active == True:
                            coupon_percentage = coupon.percentage
                            cart.get_total_price = Decimal(cart.get_total_price() - (cart.get_total_price() * (coupon_percentage / 100)))
                            cart.save()
                            return render(request, "cart/cart_summary.html", {"cart": cart, "form": form})
                            # return render(request, "cart/cart-summary.html", {"cart": cart, "form": form})
                    else:
                        return redirect("/cart/", {"error": "Coupon has expired"})
                        
                else:
                    return redirect("/cart/", {"error": "Coupon has been used by you"})
                   
            else:
                return redirect("/cart/", {"error": "Coupon is not valid"})

    return render(request, "cart/cart-summary.html", {"cart": cart, "form": form})
               

def add_to_cart(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, qty=product_qty)
        product_qty = cart.__len__()
        response = JsonResponse({"qty": product_qty})
        return response


def delete_from_cart(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        cart.delete(product=product_id)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()
        response = JsonResponse({"qty": cartqty, "subtotal": carttotal})
        return response


def update_cart(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        item_qty = int(request.POST.get("productqty"))
        cart.update(product=product_id, qty=product_qty, cartitemqty=item_qty)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()
        a_product_price = get_object_or_404(Product, id=product_id).price
        a_discount_price = get_object_or_404(Product, id=product_id).discount_price()
        if Product.objects.get(id=product_id).discount_price() < a_product_price:
            cartproductqty = item_qty * a_discount_price
        else:
            cartproductqty = item_qty * Decimal(a_product_price)
        print(cartproductqty)
        response = JsonResponse(
            {"qty": cartqty, "subtotal": carttotal, "cartproqty": cartproductqty}
        )
        return response


def clear_all_cart(request):
    cart = Cart(request)
    cart.clear()
    cartqty = cart.__len__()
    carttotal = cart.get_total_price()
    response = JsonResponse({"qty": cartqty, "subtotal": carttotal})
    return redirect("/cart/", response)
