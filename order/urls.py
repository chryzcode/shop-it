from django.urls import path
from . import views

urlpatterns = [
    path("order/<str:coupon_code>/", views.order, name="order"),
]
