from django.contrib import admin

from .models import User, store_staff

# Register your models here.

admin.site.register(User)
admin.site.register(store_staff)
