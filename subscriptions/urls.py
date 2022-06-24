from django.urls import path

from . import views

app_name = "subscriptions"

urlpatterns = [
    path(
        "initiate/<str:pk>",
        views.initiate_subscription_payment,
        name="initiate_subscription_payment",
    ),
    path(
        "verify/<str:ref>/",
        views.verify_subscription_payment,
        name="verify_subscription_payment",
    ),
    path(
        "cancel-recurring-subscription/", 
        views.cancel_recurring_subscription,
        name="cancel_recurring_subscription",
    ),
    path(
        "activate-recurring-subscription/", 
        views.activate_recurring_subscription,
        name="activate_recurring_subscription",
    )
]
