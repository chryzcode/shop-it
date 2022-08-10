import datetime
from django.utils import timezone
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
from account.models import *

from .forms import *
from .models import *
from .paystack import *
from subscriptions.models import *

from notifications.signals import notify




def generate_wallet(request, currency_code):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        if Currency.objects.filter(code=currency_code).exists():
            currency = Currency.objects.get(code=currency_code)
            if not Wallet.objects.filter(store=store, currency=currency).exists():  
                wallet = Wallet.objects.create(
                    store= store,
                    currency= currency, 
                )
                return redirect("app:store_wallet")
            else:
                messages.error(request, currency.code + ' ' + "wallet exists")
                return redirect("app:store_wallet")
        else:
            messages.error(request, "Currency not currently active")   
            return redirect("app:store_wallet")                                          
    else:
        messages.error(request, "You are not authorized")
        return redirect("app:store_wallet")





def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    cart = Cart(request)
    addresses = ""
    order = Order.objects.get(pk=pk)
    store = Store.objects.get(pk=order.store.pk)
    currency_symbol = order.currency_symbol
    currency_code = order.currency_code
    url = "https://api.countrystatecity.in/v1/countries"

    headers = {
    'X-CSCAPI-KEY': settings.COUNTRY_STATE_CITY_API_KEY
    }

    response = requests.request("GET", url, headers=headers)
    data = response.json()
    country_names = {}
    for country in data:
        country_names[country['name']] = country['iso2']
    country_names = (sorted(country_names.items(), key=lambda x: x[0]))
  
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
                    "country_names" : country_names,
                },
            )
    shipping_methods = Shipping_Method.objects.filter(store=store)
    if request.user.is_authenticated:
        if Customer.objects.filter(email=request.user.email):
            customer = Customer.objects.get(email=request.user.email)
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
                    "country_names" : country_names,
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
                "country_names" : country_names,
            },
        )


def initiate_transfer(request, account_name, account_number, amount, currency, beneficiary_name, narration):
    url = "https://api.flutterwave.com/v3/transfers"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + settings.FLUTTERWAVE_SECRET_KEY,
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
    paystack = Paystack()
    status, result = paystack.verify_payment(payment.ref, payment.amount)
    if status:
        if result["amount"] / 100 == payment.amount:
            channel = result["channel"]
            payment.verified = True
            payment.payment_method = channel
            payment.save()
    if payment.verified:
        order = Order.objects.get(pk=payment.order.pk)
        order.billing_status = True
        order.save()
        orderitems = OrderItem.objects.filter(order=order)
        for orderitem in orderitems:
            product = Product.objects.get(pk=orderitem.product.pk)
            product.availability -= orderitem.quantity
            product.save()
            if product.availability <= 5:
                staffs = store_staff.objects.filter(store=store)
                for staff in staffs:     
                    staff_user = User.objects.get(email=staff.email)
                    notify.send(store.owner, recipient=staff_user, verb="Low stock for " + product.name, product_detail_url=product.get_absolute_url())
                notify.send(store.owner, recipient=store.owner, verb="Low stock for " + product.name, product_detail_url=product.get_absolute_url())
        messages.success(request, "Verification Successful")
        cart.clear()
        if Subscription_Timeline.objects.filter(store=store).exists():
            store_subscription = Subscription_Timeline.objects.get(store=store)
            if store_subscription.subscription.name == "Professional":
                amount = payment.amount
            elif store_subscription.subscription.name == "Standard":
                amount =  int(payment.amount - (payment.amount * 0.01))
        else:
            amount = int(payment.amount - (payment.amount * 0.02))
        currency = Currency.objects.get(code=payment.order.currency_code)
        if not Wallet.objects.filter(store=store, currency=currency).exists():
            generate_wallet(request, payment.order.currency_code)
        store_wallet = Wallet.objects.get(store=store, currency=currency)
        store_wallet_amount = store_wallet.amount
        store_wallet.amount = int(amount + store_wallet_amount)
        store_wallet.save()
        Wallet_Transanction.objects.create(
            wallet = store_wallet,
            store = store,
            amount = amount,
            order = order,
        )
        staffs = store_staff.objects.filter(store=store)
        message = "Your" + ' ' + store_wallet.currency.code + ' ' + "wallet just recieved some funds"
        for staff in staffs:     
            staff_user = User.objects.get(email=staff.email)
            notify.send(store.owner, recipient=staff_user, verb=message, payment = payment.order.id) 
        notify.send(store.owner, recipient=store.owner, verb=message, payment = payment.order.id)          
        subject = f"{store.store_name} just sold some product on Shop!t"
        current_site = get_current_site(request)
        path = f"order/{order.id}"
        message = render_to_string(
            "payment/wallet-credit-alert-email.html",
            {
                "store": store,
                "domain": current_site.domain+"/"+path,
                "amount":amount,
                "currency": order.currency_symbol,
                "beneficiary_name": payment.full_name,
                "payment": payment,
            },
        )
        from_email = settings.EMAIL_HOST_USER
        to_email = [store.owner.email]
        send_mail(subject, message, from_email, to_email)

        if store_staff.objects.filter(store=store).exists():
            for staff in store_staff.filter(store=store):
                staff_email = staff.email
                send_mail(subject, message, from_email, [staff_email])

        subject = f"You just ordered some products on {store.store_name} on Shop!t platform"
        path = f"{store.slugified_store_name}/order/{order.id}"
        if payment.user in store.customers.all():
            customer = True
        else:
            customer = False
        message = render_to_string(
            "payment/order-email.html",
            {
                "store": store,
                "order": order,
                "payment": payment,
                "domain": current_site.domain+"/"+path,
                "customer": customer,
                "currency": order.currency_symbol,
            },
        )
        to_email = [payment.email]
        send_mail(subject, message, from_email, to_email)

        if Subscription_Timeline.objects.filter(store=store).exists():
            store_timeline = Subscription_Timeline.objects.get(store=store)
            if store_timeline:
                if store.country =="Nigeria" and store.state == "Lagos":
                    if payment.country =="Nigeria" and payment.state == "Lagos":
                        subject = f"{store.store_name} have a pickup delivery for you - Efdee Logistics"
                        message = render_to_string(
                            'payment/pickup-email.html',
                            {
                                'store': store,
                                'payment': payment,
                                'currency': order.currency_symbol,
                            },
                        )
                        to_email = [settings.LOGISTICS_EMAIL, store.owner.email]
                        send_mail(subject, message, from_email, to_email)

        if Customer.objects.filter(email=request.user.email, store=store).exists():
            return redirect("customer:customer_orders", store.slugified_store_name)
        else:
            return redirect("app:store", store.slugified_store_name)


def withdraw_funds(request, currency_code):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        currency = Currency.objects.get(code=currency_code)
        if Wallet.objects.filter(store=store, currency=currency).exists():
            store_wallet = Wallet.objects.get(store=store, currency=currency)
            if store_wallet:
                form = WalletForm
                if request.method == "POST":
                    form = WalletForm(request.POST)
                    amount = request.POST.get("amount")
                    if amount is None:
                        messages.error(request, "Please enter an amount")
                        return redirect("app:store_wallet")
                    if len(str(amount)) <= 3:
                        messages.error(request, "Amount for withdrawal should be more than 3 figures")
                        return redirect("app:store_wallet")
                    if str(amount).startswith(str(0)):
                        messages.error(request, "Invalid amount")
                        return redirect("app:store_wallet")
                    if form.is_valid():
                        amount = form.cleaned_data["amount"]
                        withdrawable_amount = 0
                        if Wallet_Transanction.objects.filter(wallet=store_wallet, withdraw=False).exists():
                            wallet_transanctions = Wallet_Transanction.objects.filter(wallet=store_wallet, withdraw=False)
                            for transanction in wallet_transanctions:
                                if transanction.created.weekday() > 4:
                                    payout_amount = 0
                                    withdrawable_amount += payout_amount
                                    print(withdrawable_amount)
                                    if amount > withdrawable_amount:
                                        messages.error(request, "You can not withdraw funds on weekends")
                                        return redirect("app:store_wallet")
                                else:
                                    if store_wallet.currency.code == "NGN":
                                        days_timeline = 24
                                        if transanction.created < timezone.now() - timedelta(hours=days_timeline):
                                            payout_amount = transanction.amount
                                            withdrawable_amount += payout_amount
                                            print(withdrawable_amount)
                                            if amount > withdrawable_amount:
                                                messages.error(request, "Insufficient funds")
                                                return redirect("app:store_wallet")
                                            else:
                                                narration = f"{store.store_name} just withdraw {currency.symbol}{withdrawable_amount} from {store_wallet.currency.code} wallet on Shop!t"
                                                if Bank_Info.objects.filter(store=store).exists():
                                                    store_bank = Bank_Info.objects.get(store=store)
                                                    transfer = initiate_transfer(request, store_bank.account_name, store_bank.account_number, withdrawable_amount, store_wallet.currency.code, store_bank.account_name, narration)
                                                    if transfer:
                                                        store_wallet.amount = store_wallet.amount - withdrawable_amount
                                                        store_wallet.save()
                                                        Withdrawal_Transanction.objects.create(
                                                            wallet= store_wallet,
                                                            store= store,
                                                            amount= withdrawable_amount,
                                                            account_number = store_bank.account_number,
                                                            account_name = store_bank.account_name,
                                                            account_bank = store_bank.bank_name,
                                                        )
                                                        current_site = get_current_site(request)
                                                        path = "wallet"
                                                        subject = f"{store.store_name} just withdrew funds from the  {store_wallet.currency.code} wallet on Shop!t"
                                                        message = render_to_string(
                                                            "payment/wallet-debit-alert-email.html",
                                                            {
                                                                "store": store,
                                                                "wallet": store_wallet,
                                                                "amount":withdrawable_amount,
                                                                "currency": currency.symbol,
                                                                "bank_details": store_bank,
                                                                "domain": current_site.domain+"/"+path,
                                                            },
                                                        )
                                                        from_email = settings.EMAIL_HOST_USER
                                                        to_email = [store.owner.email]
                                                        send_mail(subject, message, from_email, to_email)

                                                        if store_staff.objects.filter(store=store).exists():
                                                            for staff in store_staff.filter(store=store):
                                                                staff_email = staff.email
                                                                send_mail(subject, message, from_email, [staff_email])
                                                        messages.error(request, "Withdrawal Successful") 
                                                        return redirect("app:store_wallet")     
                                                    else:
                                                        messages.error(request, "Withdrawal Failed")
                                                        return redirect("app:store_wallet")
                                                else:
                                                    messages.error(request, "Store bank info not found") 
                                                    return redirect("app:store_wallet") 

                                        else:
                                            payout_amount = 0
                                            withdrawable_amount += payout_amount
                                            if amount > withdrawable_amount:
                                                messages.error(request, "You can not withdraw funds within 24 hours")
                                                return redirect("app:store_wallet") 
                        else:
                            messages.error(request, "No funds")   
                            return redirect("app:store_wallet")                    
                                        
                    else:
                        messages.error(request, "Form input is not valid")   
                        return redirect("app:store_wallet")  
            else:
                messages.error(request, "Wallet does not exist")
                return redirect("app:store_wallet")             
        else:
            messages.error(request, "Wallet does not exist")
            return redirect("app:store_wallet")
    else:
        messages.error(request, "You are not authorized")
        return redirect("app:store_wallet")

