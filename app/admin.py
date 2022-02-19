from django.contrib import admin

from .models import Category, Product, User

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
        "is_active",
        "created",
        "updated",
        "created_by",
        "category",
        "image_1",
        "image_2",
        "image_3",
        "description",
    ]
    list_filter = ["in_stock", "is_active"]
    list_editable = ["price", "in_stock"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(User)
