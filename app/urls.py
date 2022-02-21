from django.urls import path

from . import views

app_name = "app"

urlpatterns = [

    path('', views.home_page, name='home_page'),
    path(
        "<slugified_store_name>/all-products/",
        views.a_user_all_products,
        name="a_user_all_products",
    ),
    path(
        "<slugified_store_name>/all-categories/",
        views.a_user_all_categories,
        name="a_user_all_categories",
    ),
    path(
        "<slugified_store_name>/product-detail/<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
    path(
        "<slugified_store_name>/category-products/<slug:slug>/",
        views.a_user_category_products,
        name="a_user_category_products",
    ),
]
