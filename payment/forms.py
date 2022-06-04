from django.forms import ModelForm
from .models import *
from django import forms

class NonCustomerPaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ("full_name", "email", "phone", "address_line", "postcode", "address_line2", "city", "state", "country")

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
        }

class CustomerPaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ("full_name", "email", "phone", "use_address")

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            "use_address": forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_use_address(self):
        use_address = self.cleaned_data.get('use_address')
        if use_address is None:
            raise forms.ValidationError("Please select an address")
        return use_address

    def __init__(self, *args, **kwargs):
        super(CustomerPaymentForm, self).__init__(*args, **kwargs)
        

    
        
