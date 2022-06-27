import requests
from django.conf import settings
from payment.models import Payment


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
            payment_method = response_data["data"]["gateway_response"]["payment_method"]
            print(payment_method)
            if Payment.objects.filter(ref=ref).exists():
                payment = Payment.objects.get(ref=ref)
                payment.payment_method = payment_method
                payment.save()
            return response_data["status"], response_data["data"]
        response_data = response.json()
        return response_data["status"], response_data["message"]
