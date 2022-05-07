from django.urls import path
from . import views

app_name = "customer"

urlpatterns = [
    path("register/<slugified_store_name>/", views.customer_register, name="customer_register"),
    path("login/<slugified_store_name>/", views.customer_login, name="customer_login"),   
]
