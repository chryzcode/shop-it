import uuid

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, store_name, password, **other_fields):

        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, store_name, password, **other_fields)

    def create_user(self, email, store_name, password, **other_fields):

        if not email:
            raise ValueError(_("The email field is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, store_name=store_name, **other_fields)
        user.set_password(password)
        user.save()
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
    facebook = models.CharField(max_length=100, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)

    # for store
    store_name = models.CharField(max_length=150, unique=True)
    slugified_store_name = models.SlugField(max_length=255, unique=True)
    store_description = models.TextField(max_length=500, blank=True)
    store_image = models.ImageField(upload_to="store-images/", null=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["store_name"]

    def save(self, *args, **kwargs):
        if not self.slugified_store_name:
            self.slugified_store_name = slugify(self.store_name)
        return super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"

    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            settings.SENDER_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def __str__(self):
        return self.store_name


class store_staff(models.Model):
    full_name = models.CharField(max_length=300)
    username = models.CharField(_("username"), max_length=150, unique=True)
    slugified_username = models.SlugField(max_length=255, unique=True)
    avatar = models.ImageField(upload_to="user-profile-images/", null=True)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    store = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_staff")

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = ["store"]

    def save(self, *args, **kwargs):
        if not self.slugified_username:
            self.slugified_store_name = slugify(self.store_name)
        return super(User, self).save(*args, **kwargs)



class Address(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(User, verbose_name=_("Customer"), on_delete=models.CASCADE)
    full_name = models.CharField(_("Full Name"), max_length=150)
    phone = models.CharField(_("Phone Number"), max_length=50)
    postcode = models.CharField(_("Postcode"), max_length=50)
    address_line = models.CharField(_("Address Line 1"), max_length=255)
    address_line2 = models.CharField(_("Address Line 2"), max_length=255)
    town_city = models.CharField(_("Town/City/State"), max_length=150)
    delivery_instructions = models.CharField(_("Delivery Instructions"), max_length=255)
    country = CountryField()

    def __str__(self):
        return self.user.store_name
