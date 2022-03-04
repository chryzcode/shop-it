from django.urls import path

from . import views

urlpatterns = [
    # path('activate/<slug:uidb64>/<slug:token>)/', views.account_activate, name='activate_account'),
    path('register/', views.account_register, name='register'),
]
