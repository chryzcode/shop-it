from django import forms
from django.forms import ModelForm

from .models import *

from account.models import User

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

    def clean_email(self):
        email = self.cleaned_data["email"]
        r =  User.objects.filter(email=email)
        if r.count():
            raise forms.ValidationError("Email already exists")
        return email
    
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)