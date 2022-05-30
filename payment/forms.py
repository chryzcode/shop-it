from xml.etree.ElementInclude import include
from attr import field
from django.forms import ModelForm
from .models import *

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ("email")
