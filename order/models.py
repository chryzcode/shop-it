from django.db import models

from account.models import *
from app.models import *
from django.conf import settings
from django.utils.translation import gettext_lazy as _



# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_user", blank=True, null=True)
#     full_name = models.CharField(max_length=150)
#     email = models.EmailField(blank=True)
#     address_line = models.CharField(_("Address Line 1"), max_length=255)
#     address_line2 = models.CharField(_("Address Line 2"), max_length=255, blank=True, null=True)
#     phone = models.CharField(max_length=50)
#     country = models.CharField(_("Country"), max_length=200)
#     state = models.CharField(_("State"), max_length=200)
#     city = models.CharField(_("City"), max_length=200)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     amount = models.IntegerField(default=0)
#     payment_option = models.CharField(max_length=200, blank=True)
#     billing_status = models.BooleanField(default=False)

#     class Meta:
#         ordering = ("-created",)

#     def __str__(self):
#         return str(self.created)


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
#     price = models.DecimalField(max_digits=5, decimal_places=2)
#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):
#         return str(self.id)
