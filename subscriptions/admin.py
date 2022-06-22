from django.contrib import admin

from .models import *

admin.site.register(Subscription)
admin.site.register(Duration)
admin.site.register(Subscription_Timeline)
admin.site.register(RecurringSubscriptionData)
