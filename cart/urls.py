from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("<slugified_store_name>/", views.cart_summary, name="cart_summary"),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("delete/", views.delete_from_cart, name="delete_form_cart"),
    path("update/", views.update_cart, name="update_cart"),
    path("clear-all-cart/", views.clear_all_cart, name="clear_all_cart"),
]
