from django.forms import ModelForm
from .models import User
from django import forms
from .models import User
from django.utils.text import slugify

class RegistrationForm(ModelForm):
    check = forms.BooleanField(required=True)
    password = forms.CharField()
    password2 = forms.CharField()
    class Meta:
        model = User
        # exclude = ['avatar', 'slugified_store_name', 'country', 'post_code', 'address_line_1', 'address_line_2', 'town_city', 'is_active', 'is_staff', 'created', 'updated', 'facebook', 'instagram', 'twitter', 'phone_number' ]
        fields = ['email', 'full_name', 'store_name', "check"]

    def clean_username(self):
        store_name = self.cleaned_data['store_name'].lower()
        r = User.objects.filter(store_name=store_name)
        if r.count():
            raise forms.ValidationError("Username already exists")
        return store_name

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email is already taken')
        return email

    def clean_store_name(self):
        store_name = self.cleaned_data['store_name']
        slugified_store_name = slugify(store_name) 
        if User.objects.filter(store_name=store_name).exists() or User.objects.filter(slugified_store_name=slugified_store_name).exists():
            raise forms.ValidationError(
                'Store name is already taken')
        return store_name
        
    def __init__(self, *args, **kwargs):
            super(RegistrationForm, self).__init__(*args, **kwargs)
