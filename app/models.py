from email.policy import default

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    full_name = models.CharField(max_length=300, null=True, blank=True)
    store_name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="user-profile-images/", null=True)
    slugified_store_name = models.SlugField(max_length=255, unique=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if not self.slugified_store_name:
            self.slugified_store_name = slugify(self.store_name)
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.store_name


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

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="product", on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User, related_name="product_creator", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_1 = models.ImageField(upload_to="product-images/")
    image_2 = models.ImageField(upload_to="product-images/", default="default.jpg")
    image_3 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    image_4 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    # pulral for the table name in the admin page
    class Meta:
        verbose_name_plural = "Products"
        ordering = ("-created",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
