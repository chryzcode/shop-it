from django import forms
from django.forms import ModelForm

from .models import *


class NonCustomerPaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = (
            "full_name",
            "email",
            "phone",
            "address_line",
            "postcode",
            "address_line2",
            "state",
            "country",
        )

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "postcode": forms.TextInput(attrs={"class": "form-control"}),
            "address_line": forms.TextInput(attrs={"class": "form-control"}),
            "address_line2": forms.TextInput(attrs={"class": "form-control"}),
        }

        def clean_postcode(self):
            postcode = self.cleaned_data.get("postcode")
            if not postcode:
                raise forms.ValidationError("Please enter a valid postcode")
            return postcode

        def clean_address_line(self):
            address_line = self.cleaned_data.get("address_line")
            if not address_line:
                raise forms.ValidationError("Please enter a valid address")
            return address_line

        def clean_state(self):
            state = self.cleaned_data.get("state")
            if not state:
                raise forms.ValidationError("Please enter a valid state")
            return state

        def clean_country(self):
            country = self.cleaned_data.get("country")
            if not country:
                raise forms.ValidationError("Please enter a valid country")
            return country


class CustomerPaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = (
            "full_name",
            "email",
            "phone",
            "use_address",
            "address_line",
            "postcode",
            "address_line2",
            "state",
            "country",
        )

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "use_address": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_use_address(self):
        use_address = self.cleaned_data.get("use_address")
        if use_address is None:
            raise forms.ValidationError("Please select an address")
        return use_address

    def __init__(self, *args, **kwargs):
        super(CustomerPaymentForm, self).__init__(*args, **kwargs)


class ShippingPaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = (
            "shipping_method",
        )

    def __init__(self, *args, **kwargs):
        super(ShippingPaymentForm, self).__init__(*args, **kwargs)
        

    


class WalletForm(ModelForm):
    class Meta:
        model = Wallet
        fields = ("amount",)
        widgets = {
            "amount": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            raise forms.ValidationError("Kindly put in amount for withdrawal")
        if len(str(amount)) <= 3:
            raise forms.ValidationError(
                "Amount for withdrawal should be more than 3 figures"
            )
        if str(amount).startswith(str(0)):
            raise forms.ValidationError("Invalid amount")
        return amount

    def __init__(self, *args, **kwargs):
        super(WalletForm, self).__init__(*args, **kwargs)
