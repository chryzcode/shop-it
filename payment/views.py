from email import message
import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from app.models import *
from cart.cart import *
from customer.models import Address, Customer
from order.models import *

from .forms import *
from .models import *

RAVE_SECRET_KEY = settings.RAVE_SECRET_KEY
RAVE_PUBLIC_KEY = settings.RAVE_PUBLIC_KEY

# Create your views here.
def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    cart = Cart(request)
    addresses = ""
    order = Order.objects.get(pk=pk)
    store = Store.objects.get(pk=order.store.pk)
    currency_symbol = order.currency_symbol
    currency_code = order.currency_code
    if Payment.objects.filter(order=order).exists():
        payment = Payment.objects.get(order=order)
        if payment.verified:
            return render(
                request,
                "payment/make-payment.html",
                {
                    "payment": payment,
                    "currency_symbol": currency_symbol,
                    "currency_code": currency_code,
                    "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
                },
            )
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
            shipping_method = Shipping_Method.objects.get(id=shipping_method)
            shipping_price = shipping_method.price
            payment.order = order
            payment.amount = order.amount + shipping_price
            payment.store = store
            payment.save()
            return render(
                request,
                "payment/make-payment.html",
                {
                    "payment": payment,
                    "store": store,
                    "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
                    "currency_symbol": currency_symbol,
                    "currency_code": currency_code,
                },
            )
    else:
        payment_form = PaymentForm()
        order = Order.objects.get(pk=pk)
    return render(
        request,
        "payment/initiate-payment.html",
        {
            "payment_form": payment_form,
            "addresses": addresses,
            "shipping_methods": shipping_methods,
            "store": store,
            "order": order,
            "currency_symbol": currency_symbol,
            "currency_code": currency_code,
        },
    )


def initiate_transfer(request, account_name, account_number, amount, currency, beneficiary_name, narration):
    url = "https://api.flutterwave.com/v3/transfers"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + settings.RAVE_SECRET_KEY,
    }
    data = {
        "account_name": account_name,
        "account_number": account_number,
        "amount": amount,
        "currency": currency,
        "beneficiary_name": beneficiary_name,
        "narration": narration,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        messages.success(request, "Transfer initiated successfully")
        return response.json()
    else:
        messages.error(request, "Transfer failed")
        return response.json()


def verify_payment(request: HttpRequest, ref: str) -> HttpResponse:
    cart = Cart(request)
    payment = get_object_or_404(Payment, ref=ref)
    store = Store.objects.get(pk=payment.store.pk)
    store_bank = Bank_Info.objects.get(store=store)
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
        narration = f"{store_bank.beneficiary_name} just paid {payment.currency}{payment.amount} for some products from {store.store_name} on Shop!t"
        transfer = initiate_transfer(request, store_bank.account_name, store_bank.account_number, payment.amount, payment.currency, store_bank.beneficiary_name, narration)
        if transfer:
            messages.success(request, "Transfer initiated successfully")
            subject = f"{store.store_name} just sold some product on Shop!t"
            current_site = get_current_site(request)
            path = f"order/{order.id}"
            message = render_to_string(
                "payment/transfer-email.html",
                {
                    "store": store,
                    "domain": current_site.domain+"/"+path,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "beneficiary_name": store_bank.beneficiary_name,
                    "narration": store_bank.narration,
                },
            )
            from_email = settings.EMAIL_HOST_USER
            if store_staff.filter(store=store).exists():
                for staff in store_staff.filter(store=store):
                    staff_email = staff.email
                    send_mail(subject, message, from_email, [staff_email])
            to_email = [store.owner.email]
            send_mail(subject, message, from_email, to_email)

        else:
            messages.error(request, "Transfer failed")

    else:
        messages.error(request, "Verification Failed")
    if Customer.objects.filter(user=request.user, store=store).exists():
        return redirect("customer:customer_orders", store.slugified_store_name)
    else:
        return redirect("app:store", store.slugified_store_name)
