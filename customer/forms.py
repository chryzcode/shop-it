from django import forms
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect, render

from account.models import User

from .models import *


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["full_name", "email", "password", "password2"]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Full Name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "password": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": "Password"}
            ),
            "password2": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": "Confirm Password"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)


class ExistingUserCustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["email"]

        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
        }

        def __init__(self, *args, **kwargs):
            super(ExistingUserCustomerForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email)
        if not user:
            raise forms.ValidationError("User does not exist")
        return email


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ["customer"]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Full Name"}
            ),
            "phone": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "+349 0854 9885"}
            ),
            "postcode": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Post Code"}
            ),
            "address_line": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address Line"}
            ),
            "address_line2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Additional address(Not Compulsory)",
                }
            ),
            "delivery_instructions": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Delivery Instructions"}
            ),
            "country": forms.Select(attrs={"class": "form-control"}),
            "state": forms.Select(attrs={"class": "form-control"}),
        }
