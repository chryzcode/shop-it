from datetime import datetime, timedelta
from decimal import Decimal
from selectors import SelectorKey

from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import slugify
from pyexpat import model
from requests import request

from account.models import *
from customer.models import Customer


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
            "app:store_category_products",
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
    updated = models.DateTimeField(auto_now=True)
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
        if self.availability > 0:
            self.in_stock = True
        if self.price > int(2500):
            paystack_percentage = (1.5 * int(self.price)) / 100
            paystack_percentage = paystack_percentage + int(100)
        else:
            paystack_percentage = (1.5 * int(self.price)) / 100
        self.price = self.price + paystack_percentage
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



class Shipping_Company(models.Model):
    name = models.CharField(max_length=300)
    account_name = models.CharField(max_length=300)
    bank_code = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)


    def __str__(self):
        return self.name


class Shipping_Method(models.Model):
    shipping_company = models.ForeignKey(Shipping_Company, on_delete=models.CASCADE, default=1)
    country = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    price = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200)
    flutterwave_fund = models.PositiveIntegerField(default=0)
    shopit_fund = models.PositiveIntegerField(default=0)
    total_funds = models.PositiveIntegerField(default=0)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    state_code = models.CharField(max_length=10, blank=True, null=True)

    def save(self):
        flutterwave_fee = int(1.40/100 * self.price)
        if flutterwave_fee > 2500:
            flutterwave_fee = 2500
        self.flutterwave_fund = flutterwave_fee 
        shopit_fee =  int(2/100 * self.price)
        if shopit_fee > 2300:
            shopit_fee = 2300
        self.shopit_fund = shopit_fee
        self.total_funds =  flutterwave_fee + shopit_fee + self.price
        return super(Shipping_Method, self).save()


    def __str__(self):
        return self.location + " " + self.country + " " + self.state 


class last_7_days_sales(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "last_7_days_sales"


class last_24_hours_sales(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "last_24_hours_sales"


class last_7_days_customers(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "last_7_days_customers"


class last_24_hours_customers(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "last_24_hours_customers"


class yearly_sales(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "yearly_sales"


class last_30_days_sales(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "last_30_days_sales"


class customers_yearly(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "customers_yearly"


class customers_monthly(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    percentage = models.IntegerField(default=0)

    def __str__(self):
        return str(self.store.store_name) + " " + str(self.percentage) + "%"

    class Meta:
        verbose_name_plural = "customers_monthly"

class Store_Newsletter(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer, blank=True)

    def __str__(self):
        return str(self.store) + ' ' + 'Newsletter'

    class Meta:
        verbose_name_plural = "Store Newsletter"

class Newsletter(models.Model):
    store = models.ForeignKey(Store_Newsletter, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'A ' + str(self.store) + ' Newsletter'

    class Meta:
        verbose_name_plural = "A Store newsletters"