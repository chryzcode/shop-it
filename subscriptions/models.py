from locale import currency
from django.db import models
import secrets
from payment.paystack import Paystack
from account.models import *

# Create your models here.
class Duration(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name



class Subscription(models.Model):
    name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ref = models.CharField(max_length=200, blank=True, null=True)
    verified = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(Store, related_name="subscriptions", blank=True)
    duration = models.ForeignKey(Duration, on_delete=models.CASCADE)     
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name + ' ' + str(self.duration.name)

    def amount_value(self) -> int:
        return self.amount * 100

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result["amount"] / 100 == self.amount:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            objects_with_similar_ref = Subscription.objects.filter(ref=ref)
            if not objects_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

