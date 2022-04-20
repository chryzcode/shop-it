from decimal import Decimal

from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from account.models import User


class Category(models.Model):
    created_by = models.ForeignKey(
        User, related_name="category_creator", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    # pulral for the table name in the admin page
    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "app:a_user_category_products",
            kwargs={
                "slug": self.slug,
                "slugified_store_name": self.created_by.slugified_store_name,
            },
        )

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=20)
    percentage = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    created_by = models.ForeignKey(
        User, related_name="coupon_creator", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.IntegerField()
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, blank=True)


    def __str__(self):
        return "coupon" + self.code[:5] + "..."


class Product(models.Model):
    created_by = models.ForeignKey(
        User, related_name="product_creator", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_1 = models.ImageField(upload_to="product-images/")
    image_2 = models.ImageField(upload_to="product-images/")
    image_3 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    image_4 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category, related_name="category", on_delete=models.CASCADE
    )
    availability = models.IntegerField(default=1)
    product_details = RichTextField(null=True, blank=True, max_length=300)
    product_unit = models.ForeignKey(
        ProductUnit, related_name="product_unit", on_delete=models.CASCADE
    )
    discount_percentage = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    wishlist = models.ManyToManyField(User, related_name="wishlist", blank=True)
    coupon = models.CharField(max_length=30, null=True, blank=True)

    # pulral for the table name in the admin page
    class Meta:
        verbose_name_plural = "Products"
        ordering = ("-created",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.availability < 1:
            self.in_stock = False
        return super(Product, self).save(*args, **kwargs)

    def discount_price(self):
        if not self.discount_percentage:
            return self.price
        if self.discount_percentage:
            price = Decimal(self.price - (self.price * self.discount_percentage / 100))
            return price

    def get_absolute_url(self):
        return reverse(
            "app:product_detail",
            kwargs={
                "slug": self.slug,
            },
        )

    def __str__(self):
        return self.name
