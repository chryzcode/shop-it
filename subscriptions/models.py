from django.db import models
import secrets
from paystack.paystack import Paystack

# Create your models here.

class SubscriptionDuration(models.Model):
    duration = models.CharField(max_length=50)

    def __str__(self):
        return self.duration


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.ForeignKey(SubscriptionDuration, on_delete=models.CASCADE)
    ref = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)

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

