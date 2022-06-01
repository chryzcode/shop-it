from django.forms import ModelForm
from .models import *
from django import forms

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ("full_name", "email", "phone", "address_line", "address_line2", "city", "state", "country", "use_address", "default_address")

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            "use_address": forms.Select(attrs={'class': 'form-control'}),
            "default_address": forms.CheckboxInput(),
        }

