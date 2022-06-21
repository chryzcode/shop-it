import secrets

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from datetime import datetime, timedelta
from django.utils import timezone

from account.models import *

from .models import *


# Create your views here.
def initiate_subscription_payment(request: HttpRequest, pk) -> HttpResponse:
    if request.user.store_creator == True:
        email = request.user.email
        store = Store.objects.get(store_name=request.user.store_name)
        subscription = Subscription.objects.get(pk=pk)
        all_subscriptions = Subscription.objects.all()
        for subscription in all_subscriptions:
            if (
                store in subscription.subscribers.all()
                or subscription.subscribers.filter(pk=store.pk).exists()
            ):
                messages.error(request, "You are active on a subscription plan")
                return redirect("app:yearly_subscription_plans")
            else:
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
    verified = subscription.verify_payment()
    if verified:
        subscription.subscribers.add(store)
        Subscription_Timeline.objects.create(
            store= store,
            subscription = subscription,       
        )
        messages.success(request, "Verification Successful")
        subscription.verified = False
        subscription.ref = secrets.token_urlsafe(50)
        subscription.save()
        return redirect("app:store_admin")
    else:
        messages.error(request, "Verification Failed")

def subscription_check(request):
    store = None
    if request.user.store_creator == True:
        store = Store.objects.get(store_name=request.user.store_name)
    else:
        store = Store.objects.get(
            store_name=store_staff.objects.get(user=request.user).store
        )
    if store:
        if Subscription_Timeline.objects.get(store=store):
            subscription_timeline = Subscription_Timeline.objects.get(store=store)
            yearly_duration = Duration.objects.get(name="yearly")
            monthly_duration = Duration.objects.get(name="monthly")
            if subscription_timeline.subscription.duration ==  monthly_duration:
                # make remainder on subscriptioon finishing
                if subscription_timeline.created_at < timezone.now() - timedelta(months=1):
                    subscription = Subscription.objects.get(name = subscription_timeline.subscription.name)
                    subscription.delete()
            if subscription_timeline.subscription.duration ==  yearly_duration:
                # make remainder on subscriptioon finishing
                if subscription_timeline.created_at < timezone.now() - timedelta(months=12):
                    subscription = Subscription.objects.get(name = subscription_timeline.subscription.name)
                    subscription.delete()


