from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("initiate/<uuid:pk>/", views.initiate_payment, name="initiate_payment"),
    path("verify/<str:ref>/", views.verify_payment, name="verify_payment"),
    path("withdraw/<currency_code>/", views.withdraw_funds, name="withdraw_funds"),
    path("generate/<currency_code>/", views.generate_wallet, name="generate_wallet"),
]
