import secrets
from django.conf import settings
from django.db import models

from account.models import *
from app.models import *
from customer.models import *
from order.models import *
from django.core.mail import send_mail


# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    full_name = models.CharField(max_length=150)
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    address_line = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=50, blank=True, null=True)
    use_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    default_address = models.BooleanField(default=False, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_method = models.ForeignKey(Shipping_Method, blank=True, null=True, on_delete=models.SET_NULL)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["-date_created"]

    def __str__(self):
        return "payment" + " " + str(self.amount)

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            objects_with_similar_ref = Payment.objects.filter(ref=ref)
            if not objects_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self) -> int:
        return self.amount * 100


class Wallet(models.Model):
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="store_wallet_currency"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_wallet"
    )
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            str(self.store.store_name) + " " + str(self.currency.name) + " " + "Wallet"
        )


class Wallet_Transanction(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return (
            str(self.store.store_name)
            + " "
            + str(self.wallet.currency.code)
            + " "
            + "Wallet Transanction"
        )


class Withdrawal_Transanction(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=200)
    account_bank = models.CharField(max_length=200)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

    def email_user(self, subject, message, staff_email_list):
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.store.owner.email, staff_email_list],
            fail_silently=False,
            html_message=message
        )

    def __str__(self):
        return (
            str(self.store.store_name)
            + " "
            + str(self.wallet.currency.code)
            + " "
            + "Withdrawal Transanction"
        )
