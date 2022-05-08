from django import forms
from django.forms import ModelForm

from .models import *

from account.models import User
from django.shortcuts import get_object_or_404, redirect, render

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
