from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from cart.cart import *
from customer.models import Address, Customer
from order.models import *

from .forms import *
from django.core import serializers
json_serializer = serializers.get_serializer("json")()


# Create your views here.
def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    addresses = ""
    order = Order.objects.get(pk=pk)
    store = order.store
    shipping_methods = Shipping_Method.objects.filter(store=store)
    if request.user.is_authenticated:
        if Customer.objects.filter(user=request.user):
            customer = Customer.objects.get(user=request.user)
            addresses = Address.objects.filter(customer=customer)
            if addresses:
                PaymentForm = CustomerPaymentForm
            else:
                PaymentForm = NonCustomerPaymentForm
        else:
            PaymentForm = NonCustomerPaymentForm
    else:
        PaymentForm = NonCustomerPaymentForm
    if request.method == "POST":
        payment_form = PaymentForm(request.POST)

        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            if request.user.is_authenticated:
                payment.user = request.user
            else:
                payment.user = None
            use_address = payment_form.cleaned_data.get("use_address")
            if addresses and use_address:
                address = Address.objects.get(pk=use_address.id)
                if address:
                    payment.address_line = address.address_line
                    payment.address_line2 = address.address_line2
                    payment.postcode = address.postcode
                    payment.city = address.city
                    payment.state = address.state
                    payment.country = address.country

            if payment.country == None:
                return render(
                    request,
                    "payment/initiate-payment.html",
                    {
                        "payment_form": payment_form,
                        "order": order,
                        "shipping_methods": shipping_methods,
                        "country_error": "Field is required",
                    },
                )

            if payment.state == None:
                return render(
                    request,
                    "payment/initiate-payment.html",
                    {
                        "payment_form": payment_form,
                        "order": order,
                        "shipping_methods": shipping_methods,
                        "state_error": "Field is required",
                    },
                )

            if payment.city == None:
                return render(
                    request,
                    "payment/initiate-payment.html",
                    {
                        "payment_form": payment_form,
                        "order": order,
                        "shipping_methods": shipping_methods,
                        "city_error": "Field is required",
                    },
                )
            shipping_method = request.POST.get("shipping_method")
            shipping_method =  Shipping_Method.objects.get(id=shipping_method) 
            shipping_price = shipping_method.price
            payment.order = order
            payment.amount = order.amount + shipping_price
            payment.save()
            render(request, "payment/make-payment.html", {"payment": payment})
    else:
        payment_form = PaymentForm()
    return render(
        request,
        "payment/initiate-payment.html",
        {
            "payment_form": payment_form,
            "addresses": addresses,
            "shipping_methods": shipping_methods,
            "store": store,
        },
    )
