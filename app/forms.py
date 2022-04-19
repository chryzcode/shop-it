from django import forms
from django.forms import ModelForm

from .models import Category, Product, Coupon


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ["slug", "created_by", "created_at", "updated_at", "in_stock"]
        fields = [
            "name",
            "description",
            "image_1",
            "image_2",
            "image_3",
            "image_4",
            "price",
            "category",
            "availability",
            "product_details",
            "product_unit",
            "discount_percentage",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Product Name"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Product Description"}
            ),
            "image_1": forms.FileInput(attrs={"class": "form-control"}),
            "image_2": forms.FileInput(attrs={"class": "form-control"}),
            "image_3": forms.FileInput(attrs={"class": "form-control"}),
            "image_4": forms.FileInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Product Price"}
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "availability": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Product Availability"}
            ),
            "product_details": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Product Details"}
            ),
            "product_unit": forms.Select(
                attrs={"class": "form-control", "placeholder": "Product Unit"}
            ),
            "discount_percentage": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Product Discount"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        exclude = ["slug", "created_by"]
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category Name"}
            ),
        }
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

class CouponForm
