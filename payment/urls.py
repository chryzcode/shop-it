from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("<uuid:pk>/", views.initiate_payment, name="initiate_payment"),
]
