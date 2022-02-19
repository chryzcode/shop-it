from http.client import PROCESSING
from django.shortcuts import render
from .models import Product, User, Category


# Create your views here.

def all_products(request):
    products = Product.objects.all()
    return render(request, 'app/all_products.html', {'products': products})
