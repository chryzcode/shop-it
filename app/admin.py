from django.contrib import admin

from .models import *

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "price",
        "in_stock",
        "created",
        "updated",
        "category",
        "image_1",
        "image_2",
        "image_3",
    ]
    list_filter = ["in_stock"]
    list_editable = ["price", "in_stock"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(ProductUnit)
admin.site.register(Coupon)
admin.site.register(Review)
admin.site.register(Shipping_Method)
admin.site.register(last_7_days_sales)
admin.site.register(last_24_hours_sales)
admin.site.register(last_7_days_customers)
admin.site.register(last_24_hours_customers)
admin.site.register(yearly_sales)