from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from app.models import *

from .cart import *
from decimal import Decimal

# Create your views here.
def cart_summary(request):
    cart = Cart(request)
    return render(request, "cart/cart-summary.html", {'cart': cart})


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
        response = JsonResponse({'qty':cartqty, 'subtotal':carttotal})
        return response

def update_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        item_qty = int(request.POST.get('itemqty'))
        cart.update(product=product_id, qty=product_qty, cartitemqty=item_qty)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()   
        a_product_price = Product.objects.get(id=product_id).price
        cartproductqty = item_qty * Decimal(a_product_price )
        print(cartproductqty)
        print(product_id)
        print(a_product_price)
        print(item_qty)
        response = JsonResponse({'qty':cartqty, 'subtotal':carttotal, 'cartproqty':cartproductqty, 'productprice':a_product_price})
        return response

# clear all cart
def clear_all_cart(request):
    cart = Cart(request)
    cart.clear()
    cartqty = cart.__len__()
    carttotal = cart.get_total_price()
    response = JsonResponse({'qty':cartqty, 'subtotal':carttotal})
    return redirect('/cart/', response)