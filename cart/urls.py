from unicodedata import name
from django.urls import path

from . import views

app_name = "app"

urlpatterns = [
    path('', views.cart_summary, name="cart_summary"),
]