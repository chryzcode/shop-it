from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import *
# Create your models here.

class Customer(models.Model):
    full_name = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=300)
    password2 = models.CharField(max_length=300, default="uouos")
    store_choices = (Store.objects.all().values_list('store_name', 'store_name'))
    store = models.CharField(max_length=150, choices=store_choices)

class Address(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.CASCADE, blank=True, null=True)
    full_name = models.CharField(_("Full Name"), max_length=150)
    phone = models.CharField(_("Phone Number"), max_length=50)
    postcode = models.CharField(_("Postcode"), max_length=50)
    address_line = models.CharField(_("Address Line 1"), max_length=255)
    address_line2 = models.CharField(_("Address Line 2"), max_length=255)
    delivery_instructions = models.CharField(_("Delivery Instructions"), max_length=255)
    country = models.CharField(_("Country"), max_length=200)
    state = models.CharField(_("State"), max_length=200)

    def __str__(self):
        return self.user.store_name