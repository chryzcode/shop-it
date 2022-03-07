from django import forms
from django.forms import ModelForm
from django.utils.text import slugify


from .models import User




class RegistrationForm(ModelForm):
    check = forms.BooleanField(required=True)
    password = forms.CharField()
    password2 = forms.CharField()
    class Meta:
        model = User
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
        if User.objects.filter(slugified_store_name=slugified_store_name).exists():
            raise forms.ValidationError(
                'Store name is already taken')
        return store_name
        
    def __init__(self, *args, **kwargs):
            super(RegistrationForm, self).__init__(*args, **kwargs)

class EditAccountForm(ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'avatar', 'country', 'phone_number', 'address_line_1', 'address_line_2', 'town_city', 'instagram', 'twitter', 'facebook']

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'town_city': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
            'twitter': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
            super(EditAccountForm, self).__init__(*args, **kwargs)