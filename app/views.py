from http.client import PROCESSING
from django.shortcuts import render
from .models import Product, User, Category


# Create your views here.

def all_products(request):
    all_products = Product.objects.all()
    return render(request, 'app/all_products.html', {'all_products': all_products})

def all_categories(request):
    all_categories = Category.objects.all()
    return render(request, 'app/all_categories.html', {'all_categories': all_categories})
