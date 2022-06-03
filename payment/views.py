from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from customer.models import Address, Customer
from .forms import *
from cart.cart import *
from order.models import *

# Create your views here.
def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    address = ''
    default_address = ''
    address_count = 0
    order = Order.objects.get(pk=pk)
    shipping_methods = Shipping_Method.objects.filter(store=order.store)
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
            if request.user.is_authenticated:
                payment.user = request.user
            else:
                payment.user = None
            payment.order = order  
            if address_count:
                address = Address.objects.get(pk=payment_form.cleaned_data['address'])
                payment.address_line = address.address_line
                payment.address_line2 = address.address_line2
                payment.country = address.country
                payment.state = address.state
                payment.city = address.city         
            # payment.shipping_method = shipping_method
            # shipping_method_price = Shipping_Method.objects.get(id=shipping_method).price
            payment.amount = order.amount
            payment.save()
            render(request, 'payment/make-payment.html', {"payment":payment})
    else:
        payment_form  = PaymentForm()
    return render(request, "payment/initiate-payment.html", {"payment_form":payment_form, "address":address, "default_address":default_address, "address_count":address_count, "shipping_methods":shipping_methods})
