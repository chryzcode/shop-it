from imp import PKG_DIRECTORY
import holidays
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from notifications.signals import notify
from django.utils.text import slugify

from account.models import *
from account.views import *
from app.models import *
from cart.cart import *
from customer.models import Address, Customer
from order.models import *
from subscriptions.models import *

from .forms import *
from .models import *
from .paystack import *


def generate_wallet(request, currency_code):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        if Currency.objects.filter(code=currency_code).exists():
            currency = Currency.objects.get(code=currency_code)
            if not Wallet.objects.filter(store=store, currency=currency).exists():
                wallet = Wallet.objects.create(
                    store=store,
                    currency=currency,
                )
                return redirect("app:store_wallet")
            else:
                messages.error(request, currency.code + " " + "wallet exists")
                return redirect("app:store_wallet")
        else:
            messages.error(request, "Currency not currently active")
            return redirect("app:store_wallet")
    else:
        messages.error(request, "You are not authorized")
        return redirect("app:store_wallet")

def shipping_payment(request, pk):
    order = Order.objects.get(id=pk)
    payment = Payment.objects.get(order=order)
    shipping_methods = Shipping_Method.objects.filter(country=payment.country, state=payment.state, shipping_company=payment.store.shipping_company)
    if payment.shipping_method:
        return render(
                request,
                "payment/make-payment.html",
                {
                    "payment": payment,
                    "currency_symbol": order.currency_symbol,
                    "currency_code": order.currency_code,
                    "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
                    "store": order.store,
                },
            )
    if request.method == "POST":
        form = ShippingPaymentForm(request.POST)
        shipping_method = request.POST.get("shipping_method")
        shipping_method = Shipping_Method.objects.get(id=shipping_method)
        if form.is_valid():
            payment.shipping_method = shipping_method
            payment.amount = shipping_method.total_funds + order.amount
            payment.save()

            return render(
                request,
                "payment/make-payment.html",
                {
                    "payment": payment,
                    "store": payment.store,
                    "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
                    "currency_symbol": payment.order.currency_symbol,
                    "currency_code": payment.order.currency_code,
                },
            )
    else:
        form = ShippingPaymentForm()
    return render(request, "payment/shipping-payment.html", {"form": form, "order": order, "shipping_methods": shipping_methods, "payment":payment})


def initiate_payment(request: HttpRequest, pk) -> HttpResponse:
    cart = Cart(request)
    addresses = ""
    order = Order.objects.get(pk=pk)
    store = Store.objects.get(pk=order.store.pk)
    currency_symbol = order.currency_symbol
    currency_code = order.currency_code
    url = "https://api.countrystatecity.in/v1/countries"

    headers = {"X-CSCAPI-KEY": settings.COUNTRY_STATE_CITY_API_KEY}

    response = requests.request("GET", url, headers=headers)
    data = response.json()
    country_names = {}
    for country in data:
        country_names[country["name"]] = country["iso2"]
    country_names = sorted(country_names.items(), key=lambda x: x[0])

    if Payment.objects.filter(order=order).exists():
        payment = Payment.objects.get(order=order)
        if payment.shipping_method:
            return render(
                request,
                "payment/make-payment.html",
                {
                    "payment": payment,
                    "currency_symbol": currency_symbol,
                    "currency_code": currency_code,
                    "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
                    "country_names": country_names,
                    "store": store,
                },
            )
        else:
            return redirect("payment:shipping_payment", pk=order.id)
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
                    payment.state = address.state
                    payment.country = address.country

            if payment.country == None:
                return render(
                    request,
                    "payment/initiate-payment.html",
                    {
                        "payment_form": payment_form,
                        "order": order,
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
                        "state_error": "Field is required",
                    },
                )
            country_code = payment_form.cleaned_data["country"]
            state_code = payment_form.cleaned_data["state"]
            country = country_details(request, country_code)
            state = state_details(request, country_code, state_code)
            payment.order = order
            payment.store = store
            payment.country = country
            payment.state = state
            payment.amount = order.amount
            payment.save()
            Payment.objects.filter(order=order).exclude(id=payment.id).delete()
            return redirect("payment:shipping_payment", pk=order.id)
    else:
        payment_form = PaymentForm()
        order = Order.objects.get(pk=pk)
        return render(
            request,
            "payment/initiate-payment.html",
            {
                "payment_form": payment_form,
                "addresses": addresses,
                "store": store,
                "order": order,
                "currency_symbol": currency_symbol,
                "currency_code": currency_code,
                "country_names": country_names,
            },
        )


def initiate_transfer(
    request,
    account_name,
    account_number,
    amount,
    currency,
    beneficiary_name,
    narration,
    account_bank,
):
    url = "https://api.flutterwave.com/v3/transfers"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + settings.FLUTTERWAVE_SECRET_KEY,
    }
    data = {
        "account_name": str(account_name),
        "account_number": str(account_number),
        "amount": int(amount),
        "currency": str(currency),
        "beneficiary_name": str(beneficiary_name),
        "narration": str(narration),
        "account_bank": str(account_bank),
    }
    response = requests.request("POST", url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        messages.error(request, "verify you bank account details")
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
                    notify.send(
                        store.owner,
                        recipient=staff_user,
                        verb="Low stock availability for " + product.name,
                        product_detail_url=product.get_absolute_url(),
                    )
                notify.send(
                    store.owner,
                    recipient=store.owner,
                    verb="Low stock availability for " + product.name,
                    product_detail_url=product.get_absolute_url(),
                )
        messages.success(request, "Verification Successful")
        cart.clear()
        payment.amount =  payment.amount - payment.shipping_method.price
        payment.save()
        logistics_company = store.shipping_company
        beneficiary_name = logistics_company.account_name
        narration = f"{{payment.full_name}} just paid {{order.currency_symbol}}{{shipping_method.price}} for the logistics of order {{order.id}} in {{payment.store.store_name}} on Shopit"
        transfer = initiate_transfer(request, logistics_company.account_name, logistics_company.account_number, int(payment.shipping_method.price), order.currency_code, beneficiary_name, narration, "044")
        from_email = settings.EMAIL_HOST_USER
        if (transfer["status"] == "success"):
            subject = f"{store.store_name} have a pickup delivery for you - {logistics_company.name}"
            message = render_to_string(
                "payment/pickup-email.html",
                {
                    "store": store,
                    "payment": payment,
                    "currency": order.currency_symbol,
                    "logistics_company": logistics_company,
                },
            )
            to_email = [logistics_company.email, store.owner.email]
            send_mail(subject, message, from_email, to_email, html_message=message)
        else:
            subject = f"Logisitics fund not paid have a pickup delivery for you - {logistics_company.name}"
            message = f"""
            Logisitics funds {order.currency_symbol}{payment.shipping_method.price} made for order {order.id} on {store.store_name} has not been paid to {logistics_company.name} bank account.
            Account Number - {logistics_company.account_name}, Account Name - {logistics_company.account_name}, Account Bank - {logistics_company.bank_name}
            Pay them to deliver the {payment.address_line} {payment.address_line2}, {payment.state} State, {payment.country} Order PostCode - {payment.postcode}.
            Store Owner Contact - {store.owner.phone_number}
            Store Owner Whatsapp - {store.whatsapp}
            Store Owner Address - {store.address}
            """
            to_email = ["alabaolanrewaju13@gmail.com"]
            send_mail(subject, message, from_email, to_email, html_message=message)
            
        if Subscription_Timeline.objects.filter(store=store).exists():
            store_subscription = Subscription_Timeline.objects.get(store=store)
            if store_subscription.subscription.name == "Professional":
                amount = payment.amount
            elif store_subscription.subscription.name == "Standard":
                if payment.amount > int(2500):
                    amount = int(1/100 * payment.amount)
                    amount = amount + int(50)
                else:
                    amount = int(1/100 * payment.amount)
        else:
            if payment.amount > int(2500):
                amount = int(2/100 * payment.amount)
                amount = amount + int(50)
            else:
                amount = int(2/100 * payment.amount)
        # if amount > int(2500):
        #     paystack_percentage = (1.5 * int(amount)) / 100
        #     paystack_percentage = paystack_percentage + int(100)
        # else:
        #     paystack_percentage = (1.5 * int(amount)) / 100
        # amount = amount - paystack_percentage
        currency = Currency.objects.get(code=payment.order.currency_code)
        if not Wallet.objects.filter(store=store, currency=currency).exists():
            generate_wallet(request, payment.order.currency_code)
        store_wallet = Wallet.objects.get(store=store, currency=currency)
        store_wallet_amount = store_wallet.amount
        store_wallet.amount = int(amount + store_wallet_amount)
        store_wallet.save()
        Wallet_Transanction.objects.create(
            wallet=store_wallet,
            store=store,
            amount=amount,
            order=order,
        )
        staffs = store_staff.objects.filter(store=store)
        message = (
            store_wallet.currency.code
            + " "
            + "wallet just recieved some funds of " + currency.symbol + str(amount)
        )
        for staff in staffs:
            staff_user = User.objects.get(email=staff.email)
            notify.send(
                store.owner,
                recipient=staff_user,
                verb=message,
                payment=payment.order.id,
            )
        notify.send(
            store.owner, recipient=store.owner, verb=message, payment=payment.order.id
        )
        subject = f"{store.store_name} just sold some product on Shopit"
        message = render_to_string(
            "payment/wallet-credit-alert-email.html",
            {
                "store": store,
                "domain": settings.DEFAULT_DOMAIN,
                "amount": amount,
                "currency": order.currency_symbol,
                "beneficiary_name": payment.full_name,
                "payment": payment,
                "order": order,
            },
        )
        from_email = settings.EMAIL_HOST_USER
        to_email = [store.owner.email]
        send_mail(subject, message, from_email, to_email, html_message=message)

        if store_staff.objects.filter(store=store).exists():
            for staff in store_staff.filter(store=store):
                staff_email = staff.email
                send_mail(subject, message, from_email, [staff_email], html_message=message)

        subject = (
            f"You just ordered some products on {store.store_name} on Shopit platform"
        )
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
                "domain": settings.DEFAULT_DOMAIN,
                "customer": customer,
                "currency": order.currency_symbol,
            },
        )
        to_email = [payment.email]
        send_mail(subject, message, from_email, to_email, html_message=message)

        if Customer.objects.filter(email=request.user.email, store=store).exists():
            return redirect("customer:customer_orders", store.slugified_store_name)
        else:
            return redirect("app:store", store.slugified_store_name)


def withdraw_funds(request, currency_code):
    if request.user.store_creator == True:
        store = Store.objects.get(owner=request.user)
        store_staffs = store_staff.objects.filter(store=store)
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
                        messages.error(
                            request,
                            "Amount for withdrawal should be more than 3 figures",
                        )
                        return redirect("app:store_wallet")
                    if str(amount).startswith(str(0)):
                        messages.error(request, "Invalid amount")
                        return redirect("app:store_wallet")
                    if form.is_valid():
                        amount = form.cleaned_data["amount"]
                        if amount > store_wallet.amount:
                            messages.error(request, "Insufficient funds")
                            return redirect("app:store_wallet")
                        else:
                            withdrawable_amount = 0
                            if Wallet_Transanction.objects.filter(
                                wallet=store_wallet
                            ).exists():
                                wallet_transanctions = (
                                    Wallet_Transanction.objects.filter(
                                        wallet=store_wallet
                                    )
                                )
                                for transanction in wallet_transanctions:
                                    str_timeline = str(transanction.created).rsplit(
                                        " "
                                    )[0]

                                    if transanction.created.weekday() > 4:
                                        messages.error(
                                            request,
                                            "You can not withdraw funds on weekends",
                                        )
                                        return redirect("app:store_wallet")
                                    else:
                                        all_holidays = holidays.country_holidays("NG")
                                        if store_wallet.currency.code == "NGN":
                                            days_timeline = 24

                                        elif store_wallet.currency.code == "USD":
                                            days_timeline = 168

                                        if str_timeline not in all_holidays:
                                            if (
                                                transanction.created
                                                < timezone.now()
                                                - timedelta(hours=days_timeline)
                                            ):
                                                payout_amount = transanction.amount
                                                withdrawable_amount += payout_amount
                                                if amount > withdrawable_amount:
                                                    messages.error(
                                                        request,
                                                        f"You can withdraw only {currency.symbol}{withdrawable_amount} for now",
                                                    )
                                                    return redirect("app:store_wallet")
                                                else:
                                                    narration = f"{store.store_name} just withdraw {currency.symbol}{amount} from {store_wallet.currency.code} wallet on Shopit"
                                                    if Bank_Info.objects.filter(
                                                        store=store
                                                    ).exists():
                                                        store_bank = (
                                                            Bank_Info.objects.get(
                                                                store=store
                                                            )
                                                        )
                                                        staff_email_list = []
                                                        for staff in store_staffs:
                                                            staff_email = staff.email
                                                            staff_email_list.append(
                                                                staff_email
                                                            )

                                                        transfer = initiate_transfer(
                                                            request,
                                                            str(store_bank.account_name),
                                                            str(store_bank.account_number),
                                                            int(amount) - int(amount - (amount * 1.40)),
                                                            str(store_wallet.currency.code),
                                                            str(store_bank.account_name),
                                                            str(narration),
                                                            str(store_bank.bank_code),
                                                        )

                                                        if (
                                                            transfer["status"]
                                                            == "success"
                                                        ):
                                                            
                                                            store_wallet.amount -= (
                                                                amount 
                                                            )
                                                            store_wallet.save()
                                                            withdrawal_transanction = Withdrawal_Transanction.objects.create(
                                                                wallet=store_wallet,
                                                                store=store,
                                                                amount=amount,
                                                                account_number=store_bank.account_number,
                                                                account_name=store_bank.account_name,
                                                                account_bank=store_bank.bank_name,
                                                            )

                                                
                                                            subject = f"{store.store_name} just withdrew funds from the {store_wallet.currency.code} wallet on Shopit"
                                                            message = render_to_string(
                                                                "payment/wallet-debit-alert-email.html",
                                                                {
                                                                    "store": store,
                                                                    "wallet": store_wallet,
                                                                    "amount": amount,
                                                                    "currency": currency.symbol,
                                                                    "bank_details": store_bank,
                                                                    "domain": settings.DEFAULT_DOMAIN,
                                                                },
                                                            )
                                                            
                                                            notify.send(
                                                                store.owner,
                                                                recipient=store.owner,
                                                                verb=f"{store.store_name} just withdrew {store_wallet.currency.symbol}{amount} from the {store_wallet.currency.code} wallet on Shopit",
                                                                withdrawal_detail_url=reverse(
                                                                    "app:store_wallet"
                                                                ),
                                                            )
                                                            staffs = store_staff.objects.filter(store=store)
                                                            for a_staff in staffs:
                                                                staff_user = User.objects.get(email=a_staff.email)
                                                                notify.send(
                                                                    staff_user,
                                                                    recipient=staff_user,
                                                                    verb=f"{store.store_name} just withdrew {store_wallet.currency.symbol}{amount} from the {store_wallet.currency.code} wallet on Shopit",
                                                                    withdrawal_detail_url=reverse(
                                                                        "app:store_wallet"
                                                                    ),
                                                                )

                                                            withdrawal_transanction.email_user(
                                                                subject=subject,
                                                                message=message,
                                                                staff_email_list=staff_email_list,
                                                            )

                                                            return redirect(
                                                                "app:store_wallet"
                                                            )

                                                        else:
                                                            messages.error(
                                                                request,
                                                                "Withdrawal Failed",
                                                            )
                                                            return redirect(
                                                                "app:store_wallet"
                                                            )

                                                    else:
                                                        messages.error(
                                                            request,
                                                            "Store bank info not found",
                                                        )
                                                        return redirect(
                                                            "app:store_wallet"
                                                        )

                                            else:
                                                messages.error(
                                                    request,
                                                    "You can not withdraw funds within 24 hours",
                                                )
                                                return redirect("app:store_wallet")
                                        else:
                                            messages.error(
                                                request,
                                                "You can't withdraw on public holidays",
                                            )
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


def logistics_proposal_email(request, pk):
    order = Order.objects.get(id=pk)
    store = Store.objects.get(slugified_store_name=slugify(order.store.store_name))
    logistics = Shipping_Company.objects.get(name=store.shipping_company.name)
    order_items = OrderItem.objects.filter(order=order)
    payment =  Payment.objects.filter(order=order).last()
    Payment.objects.filter(order=order).exclude(id=payment.id).delete()
    subject = "Proposal for Parcel delivery to Unavailable Location"
    to = "Shopit"
    message = render_to_string(
            "payment/logistics-proposal-email.html",
            {
                "store": store,
                "domain": settings.DEFAULT_DOMAIN,
                "logistics": logistics,
                "order":order,
                "payment":payment,
                "order_items":order_items,
                "to": to
            },
        )
    to_email = [settings.EMAIL_HOST_USER]
    from_email = payment.email
    to = "Order Owner"
    message = render_to_string(
            "payment/logistics-proposal-email.html",
            {
                "store": store,
                "domain": settings.DEFAULT_DOMAIN,
                "logistics": logistics,
                "order":order,
                "payment":payment,
                "order_items":order_items,
                "to": to
            },
        )
    to_email = [payment.email]
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, to_email, html_message=message)
    return redirect("payment:shipping_payment", order.id)