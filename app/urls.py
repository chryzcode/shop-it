from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('<slugified_username>/all-products/', views.a_user_all_products, name='all_products'),
    path('<slugified_username>/all-categories/', views.a_user_all_categories, name='all_categories'),
    path('<slugified_username>/product-detail/<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slugified_username>/category-products/<slug:slug>/', views.a_user_category_products, name='category_products'),
]
