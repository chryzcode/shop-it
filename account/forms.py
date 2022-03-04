from django.forms import ModelForm
from .models import User
from django import forms

class RegistrationForm(ModelForm):
    password = forms.PasswordInput()
    password2 = forms.PasswordInput()
    class Meta:
        model = User
        # exclude = ['avatar', 'slugified_store_name', 'country', 'post_code', 'address_line_1', 'address_line_2', 'town_city', 'is_active', 'is_staff', 'created', 'updated', 'facebook', 'instagram', 'twitter' ]
        fields = ['email', 'full_name', 'store_name', 'phone_number',]
    
    def __init__(self, *args, **kwargs):
            super(RegistrationForm, self).__init__(*args, **kwargs)
