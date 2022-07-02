from operator import sub
import requests
from django.conf import settings
from .models import *
from app.models import *




class Paystack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    base_url = "https://api.paystack.co"

    def verify_payment(self, ref, *args, **kwargs):
        path = f"/transaction/verify/{ref}"

        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            email = response_data["data"]["customer"]["email"]
            amount = response_data["data"]["amount"]
            authorization_code = response_data["data"]["authorization"]["authorization_code"] 
            currency = response_data["data"]["currency"]
            subscription = Subscription.objects.get(ref=ref)
            store = subscription.store
            if Store.objects.filter(store_name=store.store_name).exists():
                user = Store.objects.get(store_name=store.store_name).owner
                if user.store_creator == True:
                    user = user
                    if RecurringSubscriptionData.objects.filter(store=store).exists():
                        subscription = RecurringSubscriptionData.objects.get(store=store)
                        subscription.amount = amount
                        subscription.email = email
                        subscription.authorization_code = authorization_code
                        subscription.store = store
                        subscription.currency = currency
                        subscription.save()
                    else:
                        RecurringSubscriptionData.objects.create(
                            email=email,
                            amount=amount,
                            authorization_code=authorization_code,
                            store = store,
                            currency = currency,
                        )     
            return response_data["status"], response_data["data"]
        response_data = response.json()
        return response_data["status"], response_data["message"]
