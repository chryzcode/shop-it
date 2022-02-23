from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.cart_summary, name="cart_summary"),
]