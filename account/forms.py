from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.forms import ModelForm
from django.utils.text import slugify

from .models import *


class RegistrationForm(ModelForm):
    check = forms.BooleanField(required=True)
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ["email", "store_name", "full_name", "check"]

    def clean_storename(self):
        store_name = self.cleaned_data["store_name"].lower()
        r = User.objects.filter(store_name=store_name)
        if r.count():
            raise forms.ValidationError("Store already exists")
        return store_name

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords do not match.")
        return cd["password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        r = User.objects.filter(email=email)
        if r.count():
            raise forms.ValidationError("Email is already taken")
        return email

    def clean_store_name(self):
        store_name = self.cleaned_data["store_name"]
        slugified_store_name = slugify(store_name)
        if len(store_name) == 0:
            raise forms.ValidationError("Store name cannot be empty")

        if Store.objects.filter(slugified_store_name=slugified_store_name).exists():
            raise forms.ValidationError("Store name is already taken")

        return store_name


class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = [
            "store_name",
            "store_image",
            "store_description",
            "currency",
            "country",
            "state",
            "instagram",
            "twitter",
            "facebook",
            "whatsapp",
            "address",
            "shipping_company",
        ]

        widgets = {
            "store_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "The Shop!t Store"}
            ),
            "store_image": forms.FileInput(attrs={"class": "form-control"}),
            "store_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "This is the Shop!t store for your day to day online business......",
                }
            ),
            "currency": forms.Select(attrs={"class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-control"}),
            "state": forms.Select(attrs={"class": "form-control"}),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Home Address"}
            ),
            "instagram": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://instagram.com/*******",
                }
            ),
            "twitter": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://twitter.com/*******",
                }
            ),
            "facebook": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://facebook.com/*******",
                }
            ),
            "whatsapp": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://wa.me/message/KLHFKHFKHL",
                }
            ),
            "shipping_company": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_address(self):
        address = self.cleaned_data["address"]
        if address == None:
            raise forms.ValidationError("Field is required")
        if len(address) <= 10:
            raise forms.ValidationError("Address must be more than ten characters")
        return address

    def clean_currency(self):
        currency = self.cleaned_data["currency"]
        if currency == None:
            raise forms.ValidationError("Field is required")
        return currency

    def clean_country(self):
        country = self.cleaned_data["country"]
        if country == None:
            raise forms.ValidationError("Field is required")
        return country

    def clean_state(self):
        state = self.cleaned_data["state"]
        if state == None:
            raise forms.ValidationError("Field is required")
        return state

    def clean_shipping_company(self):
        shipping_company = self.cleaned_data["shipping_company"]
        if shipping_company == None:
            raise forms.ValidationError("Field is required")
        return shipping_company

    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name",
            "avatar",
            "phone_number",
        ]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "John Doe"}
            ),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 97904095"}
            ),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if phone_number == None:
            raise forms.ValidationError("Field is required")
        return phone_number

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)


class PasswordResetForm(PasswordResetForm):
    email = forms.CharField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email)
        if not user:
            raise forms.ValidationError("Account not found")
        return email


class PasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField()
    new_password2 = forms.CharField()

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["new_password1"] != cd["new_password2"]:
            raise forms.ValidationError("Passwords do not match.")
        return cd["new_password2"]


class StoreStaffForm(ModelForm):
    class Meta:
        model = store_staff
        fields = ["full_name", "email", "phone_number", "password", "password2"]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "John Doe"}
            ),
            "email": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "johndoe@gmail.com"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 97904095"}
            ),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        r = store_staff.objects.filter(email=email)
        s = User.objects.filter(email=email, store_creator=True).exists()
        if r.count():
            raise forms.ValidationError("Email already exists")
        if s:
            raise forms.ValidationError("Store Creator can't be staff")
        return email

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords do not match.")
        return cd["password2"]

    def __init__(self, *args, **kwargs):
        super(StoreStaffForm, self).__init__(*args, **kwargs)


class ExistingStoreStaffForm(ModelForm):
    class Meta:
        model = store_staff
        fields = ["email"]

        widgets = {
            "email": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "johndoe@gmailcom"}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        r = store_staff.objects.filter(email=email)
        s = User.objects.filter(email=email, store_creator=True).exists()
        if r.count():
            raise forms.ValidationError("Email already exists")
        if s:
            raise forms.ValidationError("Store Creator can't be staff")
        return email

    def __init__(self, *args, **kwargs):
        super(ExistingStoreStaffForm, self).__init__(*args, **kwargs)


class AddStoreForm(ModelForm):
    class Meta:
        model = User
        fields = ["store_name"]

        widgets = {
            "store_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "The Shop!t Store"}
            ),
        }

    def clean_store_name(self):
        store_name = self.cleaned_data["store_name"]
        slugified_store_name = slugify(store_name)
        if len(store_name) == 0:
            raise forms.ValidationError("Store name cannot be empty")

        if Store.objects.filter(slugified_store_name=slugified_store_name).exists():
            raise forms.ValidationError("Store name is already taken")

        return store_name

    def __init__(self, *args, **kwargs):
        super(AddStoreForm, self).__init__(*args, **kwargs)


class BankForm(ModelForm):
    class Meta:
        model = Bank_Info
        fields = ["bank_name", "account_number", "account_name"]

        widgets = {
            "bank_name": forms.Select(
                attrs={"class": "form-control", "placeholder": "Bank Name"}
            ),
            "account_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Account Number"}
            ),
            "account_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Account Name"}
            ),
        }

    def clean_account_number(self):
        account_number = self.cleaned_data["account_number"]
        if len(account_number) < 10:
            raise forms.ValidationError("Account number must be 10 digits")
        return account_number

    def __init__(self, *args, **kwargs):
        super(BankForm, self).__init__(*args, **kwargs)




class ShippingCompanyForm(ModelForm):
    class Meta:
        model = Shipping_Company
        fields = ["name", "bank_name", "account_number", "account_name", "email"]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Name"}
            ),
            "bank_name": forms.Select(
                attrs={"class": "form-control", "placeholder": "Bank Name"}
            ),
            "account_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Account Number"}
            ),
            "account_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Account Name"}
            ),
            "email": forms.EmailInput(  attrs={"class": "form-control", "placeholder": "Email"
            }),
        }

    def clean_account_number(self):
        account_number = self.cleaned_data["account_number"]
        if len(account_number) < 10:
            raise forms.ValidationError("Account number must be 10 digits")
        return account_number

    def __init__(self, *args, **kwargs):
        super(ShippingCompanyForm, self).__init__(*args, **kwargs)


class ShippingMethodForm(ModelForm):
    class Meta:
        model = Shipping_Method
        fields = ["location", "price", "state" ,"country", "shipping_company"]

        widgets = {
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Location Coverage"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Price"}
            ),
            "shipping_company": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(ShippingMethodForm, self).__init__(*args, **kwargs)