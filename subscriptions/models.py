import secrets

from django.db import models

from account.models import *


# Create your models here.

def current_store_creator(request):
        if request.user.is_authenticated:
            if request.user.store_creator == True:
                return request.user
            else:
                return None
        else:
            return None

class Duration(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class Subscription(models.Model):
    name = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    description = models.TextField()
    ref = models.CharField(max_length=200, blank=True, null=True)
    verified = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(
        Store, related_name="subscriptions", blank=True
    )
    duration = models.ForeignKey(Duration, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="subscriptions", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name + " " + str(self.duration.name)

    def amount_value(self) -> int:
        return self.amount * 100

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            objects_with_similar_ref = Subscription.objects.filter(ref=ref)
            if not objects_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)


class Subscription_Timeline(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mail_remainder = models.BooleanField(default=False)

    def __str__(self):
        return str(self.subscription ) + ' ' + str(self.store.store_name) + ' ' + 'timeline'


class RecurringSubscriptionData(models.Model):
    amount = models.PositiveIntegerField()
    email = models.EmailField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    authorization_code = models.CharField(max_length=200)
    charge = models.BooleanField(default=True)
    currency = models.CharField(max_length=6)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.amount)


