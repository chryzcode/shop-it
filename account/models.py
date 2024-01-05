from locale import currency

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Shipping_Company(models.Model):
    name = models.CharField(max_length=300)
    account_name = models.CharField(max_length=300)
    bank_code = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    email = models.EmailField()


    def __str__(self):
        return self.name




class Shipping_Method(models.Model):
    shipping_company = models.ForeignKey(Shipping_Company, on_delete=models.CASCADE)
    country = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    price = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200)
    flutterwave_fund = models.PositiveIntegerField(default=0)
    shopit_fund = models.PositiveIntegerField(default=0)
    total_funds = models.PositiveIntegerField(default=0)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    state_code = models.CharField(max_length=10, blank=True, null=True)

    # def save(self):
    #     flutterwave_fee = int(1.40/100 * self.price)
    #     if flutterwave_fee > 2500:
    #         flutterwave_fee = 2500
    #     self.flutterwave_fund = flutterwave_fee 
    #     shopit_fee =  int(2/100 * self.price)
    #     if shopit_fee > 2300:
    #         shopit_fee = 2300
    #     self.shopit_fund = shopit_fee
    #     self.total_funds =  flutterwave_fee + shopit_fee + self.price 
    #     return super(Shipping_Method, self).save()


    def __str__(self):
        return self.location + " " + self.country + " " + self.state 


class Currency(models.Model):
    name = models.CharField(max_length=50, default="Nigerian Naira")
    code = models.CharField(max_length=10, default="NGN")
    symbol = models.CharField(max_length=10, default="₦")
    flutterwave_code = models.CharField(max_length=10, default="NG")

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
    store_image = models.ImageField(upload_to="store-images/", blank=True, null=True)
    currency = models.ForeignKey(
        Currency, on_delete=models.SET_NULL, null=True, blank=True
    )
    staffs = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="store_staffs", blank=True
    )
    customers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="store_customers", blank=True
    )
    facebook = models.CharField(max_length=100, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    state_code = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    shipping_company = models.ForeignKey(Shipping_Company, on_delete=models.SET_NULL, null=True, blank=True)

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

        return self.create_user(email, store_name, password, **other_fields)

    def create_user(self, email, store_name, password, **other_fields):

        if not email:
            raise ValueError(_("The email field is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, store_name=store_name, **other_fields)
        user.set_password(password)
        user.save()
        store = Store.objects.create(
            owner=user, store_name=store_name, slugified_store_name=slugify(store_name)
        )

    
        if Shipping_Company.objects.all().count() == 0:
            company = Shipping_Company.objects.create(
                name= "Olanrewaju Alaba",
                account_name="Olanrewaju Alaba",
                bank_code="058",
                bank_name="GTBank Plc",
                account_number="0844412860",
                email="alabaolanrewaju13@gmail.com",
            )

            Currency.objects.create()
        

        if Shipping_Method.objects.all().count() == 0:
            company = Shipping_Company.objects.get(email="alabaolanrewaju13@gmail.com")
            shipping_method =  Shipping_Method.objects.create(
                    shipping_company = company,
                    country = "Nigeria",
                    state="Lagos",
                    price= int(2000),
                    location="Lagos Island",
                    flutterwave_fund =  0,
                    shopit_fund =0,
                    total_funds = 0
                )
        return user


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
            html_message=message
        )

    def __str__(self):
        return self.email

    def store_name_slug(self):
        return slugify(self.store_name)


class Bank_Info(models.Model):
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=200)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
    )
    bank_code = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Bank Info"
        verbose_name_plural = "Bank Info"

    def __str__(self):
        return self.account_name


class store_staff(models.Model):
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
