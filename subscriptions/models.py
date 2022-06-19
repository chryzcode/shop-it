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
    price = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ref = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(Store, related_name="subscriptions")
    duration = models.ForeignKey(Duration, on_delete=models.CASCADE)       

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            objects_with_similar_ref = Subscription.objects.filter(ref=ref)
            if not objects_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

