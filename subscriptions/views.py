import secrets
from datetime import datetime, timedelta
from email import message

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from notifications.signals import notify

from account.models import *

from .models import *
from .paystack import Paystack

# Create your views here.


def cancel_recurring_subscription(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            recurring_subscription = RecurringSubscriptionData.objects.get(
                user=request.user
            )
            recurring_subscription.charge = False
            recurring_subscription.save()
            messages.success(request, "Recurring Subscription Cancelled")
            return redirect("app:store_admin")
        else:
            return redirect("/")
    return redirect("/")


def activate_recurring_subscription(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            recurring_subscription = RecurringSubscriptionData.objects.get(
                user=request.user
            )
            recurring_subscription.charge = True
            recurring_subscription.save()
            messages.success(request, "Recurring Subscription Activated")
            return redirect("app:store_admin")
        else:
            return redirect("/")
    return redirect("/")


def initiate_subscription_payment(request: HttpRequest, pk) -> HttpResponse:
    if request.user.store_creator == True:
        email = request.user.email
        store = Store.objects.get(store_name=request.user.store_name)
        subscription = Subscription.objects.get(pk=pk)
        subscription.user = request.user
        subscription.save()
        if Subscription_Timeline.objects.filter(store=store):
            subscription_timeline = Subscription_Timeline.objects.filter(
                store=store
            ).first()
            subscription_timeline.delete()
            return redirect("subscriptions:initiate_subscription_payment", pk=pk)

        return render(
            request,
            "subscriptions/make-subscription-payments.html",
            {
                "subscription": subscription,
                "store": store,
                "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
                "email": email,
            },
        )
    else:
        return redirect("/")


def verify_subscription_payment(request: HttpRequest, ref: str) -> HttpResponse:
    subscription = get_object_or_404(Subscription, ref=ref)
    store = Store.objects.get(store_name=request.user.store_name)
    subscriptions = Subscription.objects.all()
    paystack = Paystack()
    status, result = paystack.verify_payment(subscription.ref, subscription.amount)
    if status:
        if result["amount"] / 100 == subscription.amount:
            subscription.verified = True
            subscription.user = request.user
            subscription.save()
    if subscription.verified:
        for subscription in subscriptions:
            if store in subscription.subscribers.all():
                subscription.subscribers.remove(store)
                subscription.save()
        subscription.subscribers.add(store)
        Subscription_Timeline.objects.create(
            store=store,
            subscription=subscription,
        )
        messages.success(request, "Verification Successful")
        message = f"{store.store_name} has succesfully subscribed to a plan"
        staffs = store_staff.objects.filter(store=store)
        for staff in staffs:
            staff_user = User.objects.get(email=staff.email)
            notify.send(
                store.owner,
                recipient=staff_user,
                verb=message,
                subscription=subscription.id,
            )
        notify.send(
            store.owner,
            recipient=store.owner,
            verb=message,
            subscription=subscription.id,
        )
        subject = f"Your {subscription.name} {subscription.duration.name} Subscription on Shopit has been Activated"
        message = render_to_string(
            "subscriptions/subscription-success-mail.html",
            {
                "store": store,
                "subscription": subscription,
            },
        )
        from_email = settings.EMAIL_HOST_USER
        to_email = [request.user.email]
        send_mail(subject, message, from_email, to_email, html_message=message)
        if store_staff.objects.filter(store=store).exists():
            for staff in store_staff.objects.filter(store=store):
                if staff.user.email:
                    to_email = [staff.user.email]
                    send_mail(subject, message, from_email, to_email, html_message=message)
        subscription.verified = False
        subscription.user = None
        subscription.ref = secrets.token_urlsafe(50)
        subscription.save()
        return redirect("app:store_admin")
    else:
        messages.error(request, "Verification Failed")


def paystack_recurring_payment(request: HttpRequest, pk) -> HttpResponse:
    if RecurringSubscriptionData.objects.get(user=request.user).charge == True:
        base_url = "https://api.paystack.co/transaction/charge_authorization"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        recurring_subscription_data = RecurringSubscriptionData.objects.get(
            user=request.user
        )
        data = {
            "authorization_code": recurring_subscription_data.authorization_code,
            "email": recurring_subscription_data.email,
            "amount": recurring_subscription_data.amount,
            "currency": recurring_subscription_data.currency,
        }
        response = requests.request("POST", base_url, headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()
            if data["data"]["status"] == "success":
                subscription = Subscription.objects.get(pk=pk)
                subscription.verified = True
                subscription.save()
                subscription.subscribers.add(
                    Store.objects.get(store_name=request.user.store_name)
                )
                if Subscription_Timeline.objects.filter(
                    store=Store.objects.get(store_name=request.user.store_name)
                ).exists():
                    subscription_timeline = Subscription_Timeline.objects.get(
                        store=Store.objects.get(store_name=request.user.store_name)
                    )
                    subscription_timeline.store = Store.objects.get(
                        store_name=request.user.store_name
                    )
                    subscription_timeline.subscription = subscription
                    subscription_timeline.mail_remainder = False
                    subscription_timeline.save()
                else:
                    Subscription_Timeline.objects.create(
                        store=Store.objects.get(store_name=request.user.store_name),
                        subscription=subscription,
                        mail_remainder=False,
                    )
                messages.success(request, "Subscription Successful")
                store = Store.objects.get(store_name=request.user.store_name)
                message = (
                    f"{store.store_name} just resubscribed to a plan(recurring sub)"
                )
                staffs = store_staff.objects.filter(store=store)
                for staff in staffs:
                    staff_user = User.objects.get(email=staff.email)
                    notify.send(
                        store.owner,
                        recipient=staff_user,
                        verb=message,
                        subscription=subscription.id,
                    )
                notify.send(
                    store.owner,
                    recipient=store.owner,
                    verb=message,
                    subscription=subscription.id,
                )
                subject = f"Your {subscription.name} {subscription.duration.name} Subscription on Shopit has been Re-Activated"
                message = render_to_string(
                    "subscriptions/recurring-subscription-success-mail.html",
                    {
                        "store": Store.objects.get(store_name=request.user.store_name),
                        "subscription": subscription,
                        "domain": settings.DEFAULT_DOMAIN,
                    },
                )
                from_email = settings.EMAIL_HOST_USER
                to_email = [request.user.email]
                send_mail(subject, message, from_email, to_email, html_message=message)
                if store_staff.objects.filter(
                    store=Store.objects.get(store_name=request.user.store_name)
                ).exists():
                    for staff in store_staff.objects.filter(
                        store=Store.objects.get(store_name=request.user.store_name)
                    ):
                        if staff.user.email:
                            to_email = [staff.user.email]
                            send_mail(subject, message, from_email, to_email, html_message=message)

                subscription.verified = False
                subscription.user = None
                subscription.ref = secrets.token_urlsafe(50)
                subscription.save()
                return redirect("app:store_admin")
            else:
                messages.error(request, "Subscription Failed")
        else:
            messages.error(request, "Subscription Failed")


def subscription_check_mail_remainder(request):
    for store in Store.objects.all():
        if Subscription_Timeline.objects.filter(
            store=store, mail_remainder=False
        ).exists():
            subscription_timeline = Subscription_Timeline.objects.filter(
                store=store
            ).first()
            yearly_duration = Duration.objects.get(name="yearly")
            monthly_duration = Duration.objects.get(name="monthly")
            if subscription_timeline.subscription.duration == monthly_duration:
                if subscription_timeline.created_at < timezone.now() - timedelta(
                    days=25
                ):
                    subject = "Your Shopit Monthly Subscription is about to Expire"
                    store_owner = store.owner
                    message = render_to_string(
                        "subscriptions/subscription-mail-remainder.html",
                        {
                            "store": store,
                            "duration": "monthly",
                            "domain": settings.DEFAULT_DOMAIN,
                        },
                    )
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [store_owner.email]
                    send_mail(subject, message, from_email, to_email, html_message=message)
                    if store_staff.objects.filter(store=store).exists():
                        for staff in store_staff.objects.filter(store=store):
                            if staff.user.email:
                                to_email = [staff.user.email]
                                send_mail(subject, message, from_email, to_email, html_message=message)
                    subscription_timeline.mail_remainder = True
                    subscription_timeline.save()

            if subscription_timeline.subscription.duration == yearly_duration:
                if subscription_timeline.created_at < timezone.now() - timedelta(
                    days=355
                ):
                    subject = "Your Shopit Yearly Subscription is about to Expire"
                    store_owner = store.owner
                    message = message = render_to_string(
                        "subscriptions/subscription-mail-remainder.html",
                        {
                            "store": store,
                            "duration": "yearly",
                            "domain": settings.DEFAULT_DOMAIN,
                        },
                    )
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [request.user.email]
                    send_mail(subject, message, from_email, to_email, html_message=message)
                    if store_staff.objects.filter(store=store).exists():
                        for staff in store_staff.objects.filter(store=store):
                            if staff.user.email:
                                to_email = [staff.user.email]
                                send_mail(subject, message, from_email, to_email, html_message=message)
                    subscription_timeline.mail_remainder = True
                    subscription_timeline.save()


def subscription_check(request):
    for store in Store.objects.all():
        if Subscription_Timeline.objects.filter(store=store).exists():
            subscription_timeline = Subscription_Timeline.objects.filter(
                store=store
            ).first()
            yearly_duration = Duration.objects.get(name="yearly")
            monthly_duration = Duration.objects.get(name="monthly")
            recurring_subscription_data = RecurringSubscriptionData.objects.get(
                user=store.owner
            )
            if subscription_timeline.subscription.duration == monthly_duration:
                if subscription_timeline.created_at < timezone.now() - timedelta(
                    days=30
                ):
                    subscription = Subscription.objects.get(
                        name=subscription_timeline.subscription.name,
                        duration=monthly_duration,
                    )
                    if recurring_subscription_data.charge == True:
                        paystack_recurring_payment(request, subscription.pk)
                    else:
                        subscription.subscribers.remove(store)
                        subscription_timeline.delete()
                        messages.success(
                            request, "Your monthly subscription has expired"
                        )
            if subscription_timeline.subscription.duration == yearly_duration:
                if subscription_timeline.created_at < timezone.now() - timedelta(
                    days=365
                ):
                    subscription = Subscription.objects.get(
                        name=subscription_timeline.subscription.name,
                        duration=yearly_duration,
                    )
                    if recurring_subscription_data.charge == True:
                        paystack_recurring_payment(request, subscription.pk)
                    else:
                        subscription.subscribers.remove(store)
                        subscription_timeline.delete()
                        messages.success(
                            request, "Your yearly subscription has expired"
                        )
