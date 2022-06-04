from locale import currency
from operator import mod

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Currency(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name

class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_owner"
    )
    store_name = models.CharField(max_length=150, unique=True)
    slugified_store_name = models.SlugField(max_length=255, unique=True)
    store_description = models.TextField(max_length=500, blank=True)
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_NULL, blank=True, null=True, default=None
    )
    store_image = models.ImageField(upload_to="store-images/")
    staffs = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="store_staffs", blank=True)
    customers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="store_customers", blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    def save(self, *args, **kwargs):
        self.slugified_store_name = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.store_name

class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, store_name, password, **other_fields):

        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")
       
        email = self.normalize_email(email)
        user = self.model(email=email, store_name=store_name, **other_fields)
        user.set_password(password)
        user.save()
        store = Store.objects.create(
            store_name=store_name,
            owner= user,
        )


        return self.create_user(email, store_name, password, **other_fields)

    def create_user(self, email, store_name, password, **other_fields):

        if not email:
            raise ValueError(_("The email field is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, store_name=store_name, **other_fields)
        user.set_password(password)
        user.save()
        store = Store.objects.create(
            owner=user,
            store_name=store_name,
        )
        return user


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(max_length=300)
    avatar = models.ImageField(upload_to="user-profile-images/", null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    store_name = models.CharField(max_length=150, blank=True, null=True)
    store_creator = models.BooleanField(default=True)
    store_staff = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["store_name"]

    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
        )

    def __str__(self):
        return self.email

    def store_name_slug(self):
        return slugify(self.store_name)


class Bank_Info(models.Model):
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Bank Info"
        verbose_name_plural = "Bank Info"

    def __str__(self):
        return self.name


class store_staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    full_name = models.CharField(max_length=300)
    email = models.EmailField(_("email"))
    avatar = models.ImageField(upload_to="user-profile-images/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=100)
    password2 = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="store")

    class Meta:
        verbose_name = "Store Staff"
        verbose_name_plural = " Store Staffs"

    def __str__(self):
        return self.full_name


class Shipping_Method(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="shipping_method"
    )
    location = models.CharField(max_length=250)
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.location + " " + self.store.store_name
