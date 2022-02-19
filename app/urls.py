from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('all-products/<slugified_username>/', views.all_products, name='all_products'),

]
