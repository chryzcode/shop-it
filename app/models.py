from turtle import mode, update
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = models.CharField(max_length=300, null=True, blank=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="user-profile-images/", null=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    # pulral for the table name in the admin page
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='product_creator', on_delete=models.CASCADE)
    name = models.CharField(max_length= 255)
    description = models.TextField()
    image_1 = models.ImageField(upload_to="product-images/", null=True)
    image_2 = models.ImageField(upload_to="product-images/")
    image_3 = models.ImageField(upload_to="product-images/")
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    # pulral for the table name in the admin page
    class Meta:
        verbose_name_plural = "Products"
        ordering = ('-created',)

    def __str__(self):
        return self.name
