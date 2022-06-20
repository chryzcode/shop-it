from datetime import datetime, timedelta
from decimal import Decimal

from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import slugify
from pyexpat import model
from requests import request

from account.models import *


class Category(models.Model):
    created_by = models.ForeignKey(Store, on_delete=models.CASCADE)
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
            "app:a_store_category_products",
            kwargs={
                "slug": self.slug,
                "slugified_store_name": slugify(self.created_by),
            },
        )

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Coupon(models.Model):
    code = models.CharField(max_length=20, blank=True, null=True)
    percentage = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    created_by = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.IntegerField()

    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return "coupon" + " " + self.code[:5] + "..."


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_1 = models.ImageField(upload_to="product-images/")
    image_2 = models.ImageField(upload_to="product-images/")
    image_3 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    image_4 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    price = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products_category"
    )
    availability = models.IntegerField(default=1)
    product_details = RichTextField(null=True, blank=True, max_length=300)
    product_unit = models.ForeignKey(
        ProductUnit, related_name="product_unit", on_delete=models.CASCADE
    )
    discount_percentage = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    wishlist = models.ManyToManyField(User, related_name="wishlist", blank=True)
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Products"
        ordering = ("-created",)

    def save(self, *args, **kwargs):
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


class Review(models.Model):
    title = models.CharField(max_length=200)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    comment = models.TextField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Reviews"
        ordering = ("-created",)

    def __str__(self):
        return self.title + " " + self.full_name + " " + self.store.store_name
