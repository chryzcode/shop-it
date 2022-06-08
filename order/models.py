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
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    coupon = models.BooleanField(default=False)
    

    class Meta:
        ordering = ("-created",)

    def set_product(self, product):
        self.product.add(product)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"



