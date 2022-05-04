import email
from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.forms import ModelForm
from django.utils.text import slugify

from .models import User, store_staff, Store


class RegistrationForm(ModelForm):
    check = forms.BooleanField(required=True)
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        models = User
        fields = ["email", "store_name", "full_name", "check"]

    def clean_username(self):
        store_name = self.cleaned_data["store_name"].lower()
        r = User.objects.filter(store_name=store_name)
        if r.count():
            raise forms.ValidationError("Username already exists")
        return store_name

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords do not match.")
        return cd["password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already taken")
        return email

    def clean_store_name(self):
        store_name = self.cleaned_data["store_name"]
        slugified_store_name = slugify(store_name)
        if Store.objects.filter(slugified_store_name=slugified_store_name).exists():
            raise forms.ValidationError("Store name is already taken")
        return store_name

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = [
            "store_name", 
            "store_image",
            "store_description",
        ]

        widgets = {
            "store_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "The Shop!t Store"}
            ),
            "store_image": forms.FileInput(attrs={"class": "form-control"}),
            "store_description": forms.Textarea(attrs={"class": "form-control", "placeholder":"This is the Shop!t store for your day to day online business......"}),
        }

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name",
            "avatar",
            "instagram",
            "twitter",
            "facebook",
            "phone_number",
        ]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "John Doe"}
            ),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            # 'country': forms.Select(attrs={'class': 'form-control'}),
            # 'post_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'256785'}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 97904095"}
            ),
            # 'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Block 235 Washington DC'}),
            # 'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder':''}),
            # 'town_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Texas'}),
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
        }

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
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "John Doe"}),
            "email": forms.TextInput(attrs={"class": "form-control", "placeholder": "johndoe@gmail.com"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+1 97904095"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        username = self.cleaned_data["email"]
        r = store_staff.objects.filter(email=email)
        if r.count():
            raise forms.ValidationError("Email already exists")
        return username

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords do not match.")
        return cd["password2"]

    def __init__(self, *args, **kwargs):
        super(StoreStaffForm, self).__init__(*args, **kwargs)
