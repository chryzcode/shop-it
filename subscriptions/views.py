from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import *
from account.models import *
from django.conf import settings
from django.contrib import messages
import secrets

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
        messages.success(request, "Verification Successful")
        subscription.verified = False
        subscription.ref = secrets.token_urlsafe(50)
        subscription.save()
        return redirect("app:store_admin")
    else:
        messages.error(request, "Verification Failed")
