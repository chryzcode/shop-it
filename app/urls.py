from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('<slugified_username>/all-products/', views.all_products, name='all_products'),
    path('<slugified_username>/all-categories/', views.all_categories, name='all_categories'),
    path('<slugified_username>/product-detail/<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slugified_username>/category-products/<slug:slug>/', views.category_products, name='category_products'),
]
