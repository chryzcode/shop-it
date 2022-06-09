from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib import messages

from cart.cart import *
from customer.models import Address, Customer
from order.models import *
from .models import *

from .forms import *
from django.core import serializers
json_serializer = serializers.get_serializer("json")()


# Create your views here.
def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    addresses = ""
    order = Order.objects.get(pk=pk)
    store = Store.objects.get(pk=order.store.pk)
    currency = Currency.objects.get(pk=store.currency.pk)
    if Payment.objects.filter(order=order).exists():
        payment = Payment.objects.get(order=order)
        if payment.verified:
            return render(request, "payment/make-payment.html", {"payment": payment, "store":store, "paystack_public_key":settings.PAYSTACK_PUBLIC_KEY})
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
            payment.currency = currency
            payment.store = store
            payment.save()
            return render(request, "payment/make-payment.html", {"payment": payment, "store":store, "paystack_public_key":settings.PAYSTACK_PUBLIC_KEY})
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

def verify_payment(request: HttpRequest, ref:str) -> HttpResponse:
    cart = Cart(request)
    payment = get_object_or_404(Payment, ref=ref)
    store = Store.objects.get(pk=payment.store.pk)
    verified = payment.verify_payment()
    if verified:
        order = Order.objects.get(pk=payment.order.pk)
        order.billing_status = True
        order.save()
        orderitems = OrderItem.objects.filter(order=order)
        for orderitem in orderitems:
            product = Product.objects.get(pk=orderitem.product.pk)
            product.availability -= orderitem.quantity
            product.save()
        messages.success(request, "Verification Successful")
        cart.clear()
    else:
        messages.error(request, "Verification Failed")
    if Customer.objects.filter(user=request.user, store=store).exists():
        return redirect("customer:customer_orders", store.slugified_store_name)
    else:
        return redirect("app:store", store.slugified_store_name)