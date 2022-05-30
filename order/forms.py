from django.forms import ModelForm
from .models import *

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'address_line', 'address_line2', 'phone', 'country', 'state', 'city']