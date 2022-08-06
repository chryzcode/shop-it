from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Payment)
admin.site.register(Wallet)
admin.site.register(Wallet_Transanction)
admin.site.register(Withdrawal_Transanction)
