from django.db import models
import uuid
from account.models import *
from app.models import *




class Order(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    amount = models.IntegerField(default=0)
    billing_status = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0)
    product = models.ManyToManyField(Product, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created",)



