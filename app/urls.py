from django.urls import path

from . import views

app_name = "app"


urlpatterns = [
    path("", views.home_page, name="base"),
    path("create-product/", views.create_product, name="create_product"),
    path("edit/product/<slug>", views.edit_product, name="edit_product"),
    path("delete/product/<slug>", views.delete_product, name="delete_product"),
    path("add-wishlist/<slug>", views.add_wishlist, name="add_wishlist"),
    path("remove-wishlist/<slug>", views.remove_wishlist, name="remove_wishlist"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path(
        "products/",
        views.a_user_all_products,
        name="store_products",
    ),
    path(
        "<slugified_store_name>/all-categories/",
        views.a_user_all_categories,
        name="a_user_all_categories",
    ),
    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
    path(
        "<slugified_store_name>/category-products/<slug:slug>/",
        views.a_user_category_products,
        name="a_user_category_products",
    ),
    path("home/", views.store_overview, name="store_overview"),
    path("categories/", views.all_category, name="all_category"),
    path("create-category/", views.add_category, name="create_category"),
    path("edit-category/<slug:slug>/", views.edit_category, name="edit_category"),
    path("delete-category/<slug:slug>/", views.delete_category, name="delete_category"),
    path("discount-products/", views.discount_products, name="discount_products"),
    path("coupon/", views.all_coupons, name="all_coupons"),
    path("create-coupon/", views.create_coupon, name="create_coupon"),
    path("delete-coupon/<str:pk>/", views.delete_coupon, name="delete_coupon"),
]
