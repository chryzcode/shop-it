from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from customer.models import Address, Customer
from .forms import *
from cart.cart import *
from order.models import *

# Create your views here.
def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    order = Order.objects.get(pk=pk)
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user) 
        if customer:
            address_count = Address.objects.filter(customer=customer).count() > 1
            address = Address.objects.filter(customer=customer)
            default_address = Address.objects.filter(customer=customer, default=True)
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            shipping_method= payment_form.cleaned_data["shipping_method"]
            if request.user.is_authenticated:
                payment.user = request.user
                if address:
                    payment.address_line = address.address_line
                    payment.address_line2 = address.address_line2
                    payment.city = address.city
                    payment.state = address.state
                    payment.country = address.country
                if default_address:
                    payment.address_line = default_address.address_line
                    payment.address_line2 = default_address.address_line2
                    payment.city = default_address.city
                    payment.state = default_address.state
                    payment.country = default_address.country
            payment.order = order
            payment.shipping_method = shipping_method
            shipping_method_price = Shipping_Method.objects.get(id=shipping_method).price
            payment.amount = int(order.amount + shipping_method_price)
            payment.save()
            render(request, 'payment/make-payment.html', {"payment":payment})
    else:
        payment_form  = PaymentForm()
    return render(request, "payment/initiate-payment.html", {"payment_form":payment_form, "address":address, "default_address":default_address, "address_count":address_count})
