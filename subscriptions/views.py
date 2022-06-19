from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse
from .models import *
from account.models import *
from django.conf import settings

# Create your views here.
def initiate_subscription_payment(request: HttpRequest, pk) -> HttpResponse:
    if request.user.store_creator == True:
        email = request.user.email
        store = Store.objects.get(store_name=request.user.store_name)
        subscription = Subscription.objects.get(pk=pk)
        if subscription.subscribers.filter(pk=store.pk).exists():
            return redirect("/")
        else:
            return render(request, "subscriptions/make-subscription-payments.html", 
                {"subscription": subscription, "store": store, "paystack_public_key":settings.PAYSTACK_PUBLIC_KEY, "email":email}
            )
    else:
        return redirect("/")

