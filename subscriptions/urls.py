from django.urls import path
from . import views

app_name="subscriptions"

urlpatterns = [
    path("<str:pk>", views.initiate_subscription_payment, name="initiate_subscription_payment"),
    path("<str:ref>/", views.verify_subscription_payment, name="verify_subscription_payment"),
]
