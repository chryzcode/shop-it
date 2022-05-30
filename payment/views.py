from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .forms import *

# Create your views here.
def initiate_paymemt(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save()
            render(request, 'payment/make-payment.html', {"payment":payment})
    else:
        payment_form  = PaymentForm()
    return render(request, "initiate-payment.html", {"payment_form":payment_form})
