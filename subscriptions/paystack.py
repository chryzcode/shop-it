from operator import sub
import requests
from django.conf import settings
from recurringpayment.models import RecurringSubscriptionData
from .models import Subscription




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
            subscription = Subscription.objects.get(ref=ref)
            user = subscription.user
            if user.is_authenticated:
                if user.store_creator == True:
                    user = user
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
            return response_data["status"], response_data["data"]
        response_data = response.json()
        return response_data["status"], response_data["message"]
