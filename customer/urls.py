from django.urls import path
from . import views

app_name = "customer"

urlpatterns = [
    path("register/<slugified_store_name>/", views.customer_register, name="customer_register"),
    path("login/<slugified_store_name>/", views.customer_login, name="customer_login"),
    path("register/existing-user/<slugified_store_name>/", views.existing_user_customer_register, name="existing_user_customer_register"),   
    path("<slugified_store_name>/logout", views.customer_logout, name="customer_logout"),
    path("<slugified_store_name>/product/<slug:slug>/", views.customer_product_detail, name="customer_product_detail"),
    path("<slugified_store_name>/profile/", views.customer_profile, name="customer_profile"),
]
