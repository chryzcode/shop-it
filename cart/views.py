from itertools import product
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .cart import *
from app.models import *

# Create your views here.
def cart_summary(request):
    return render(request, 'cart/cart-summary.html')

def add_to_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, qty=product_qty)
        response = JsonResponse({'qty': product_qty})
        return response
