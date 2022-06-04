from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    path("<str:coupon_code>/", views.order, name="create_order"),
]
