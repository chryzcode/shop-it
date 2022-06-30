from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("initiate/<uuid:pk>/", views.initiate_payment, name="initiate_payment"),
    path("verify/<str:ref>/", views.verify_payment, name="verify_payment"),
]
