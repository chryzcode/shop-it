from django.urls import path

from . import views

app_name = "customer"

urlpatterns = [
    path(
        "register/<slugified_store_name>/",
        views.customer_register,
        name="customer_register",
    ),
    path("login/<slug:slugified_store_name>/", views.customer_login, name="customer_login"),
    path(
        "logout/<slugified_store_name>/", views.customer_logout, name="customer_logout"
    ),
    path(
        "register/existing-user/<slugified_store_name>/",
        views.existing_user_customer_register,
        name="existing_user_customer_register",
    ),
    path(
        "<slugified_store_name>/logout", views.customer_logout, name="customer_logout"
    ),
    path(
        "<slugified_store_name>/product/<slug:slug>/",
        views.customer_product_detail,
        name="customer_product_detail",
    ),
    path(
        "<slugified_store_name>/profile/",
        views.customer_profile,
        name="customer_profile",
    ),
    path(
        "<slugified_store_name>/wishlist/",
        views.customer_wishlist,
        name="customer_wishlist",
    ),
    path(
        "add-wishlist/<slug>", views.customer_add_wishlist, name="customer_add_wishlist"
    ),
    path(
        "remove-wishlist/<slug>",
        views.customer_remove_wishlist,
        name="customer_remove_wishlist",
    ),
    path("<slugified_store_name>/address/", views.address_list, name="address_list"),
    path(
        "<slugified_store_name>/address/create/",
        views.create_address,
        name="create_address",
    ),
    path(
        "<slugified_store_name>/set-default/address/<str:id>/",
        views.set_default_address,
        name="set_default_address",
    ),
    path(
        "<slugified_store_name>/edit/address/<str:id>/",
        views.edit_address,
        name="edit_address",
    ),
    path(
        "<slugified_store_name>/delete/address/<str:id>/",
        views.delete_address,
        name="delete_address",
    ),
    path("stores/", views.customer_stores, name="customer_stores"),
    path("<slugified_store_name>/delete", views.delete_account, name="delete_account"),
    path("<slugified_store_name>/orders/", views.customer_orders, name="customer_orders"),
    path("<slugified_store_name>/order/<uuid:pk>/", views.customer_order_detail, name="customer_order_detail"),
]
