import requests
from django.conf import settings
from .views import CreateRecurringSubscriptionDataFunction

class Paystack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    base_url = "https://api.paystack.co"


    def verify_payment(self, request, ref, *args, **kwargs):
        path = f"/transaction/verify/{ref}"

        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            print(response_data)          
            email = response_data["data"]["customer"]["email"],
            amount = response_data["data"]["amount"],
            authorization_code = response_data["data"]["authorization_code"],
            CreateRecurringSubscriptionDataFunction(request, email, amount, authorization_code)
            return response_data["status"], response_data["data"]
        response_data = response.json()
        return response_data["status"], response_data["message"]
