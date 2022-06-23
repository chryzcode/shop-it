from locale import currency
from django.db import models
from django.conf import settings
# Create your models here.
class RecurringSubscriptionData(models.Model):
    amount = models.PositiveIntegerField()
    email = models.EmailField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    authorization_code = models.CharField(max_length=200)
    charge = models.BooleanField(default=True)
    currency = models.CharField(max_length=6)

    def __str__(self):
        return str(self.user.store_name) + " " + str(self.user.full_name) + " " + str(self.amount)


        