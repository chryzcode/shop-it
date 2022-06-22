from django.shortcuts import render
from .models import RecurringSubscriptionData
from django.conf import settings

def check(request, amount, authorization_code, email):
    if request.user.is_authenticated:
        if request.user.store_creator == True:
            user = request.user
            if RecurringSubscriptionData.objects.filter(user=user).exists():
                subscription = RecurringSubscriptionData.objects.get(user=user)
                subscription.amount = amount
                subscription.email = email
                subscription.authorization_code = authorization_code
                subscription.user = user
                subscription.save()
            else:
                RecurringSubscriptionData.objects.create(
                    email=email,
                    amount=amount,
                    authorization_code=authorization_code,
                    user = user,
                )

    