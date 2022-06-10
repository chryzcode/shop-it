from venv import create
from attr import fields

from django import forms
from django.forms import ModelForm

from .models import Category, Coupon, Product, Review


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

    def clean_product_name(self):
        name = self.cleaned_data.get("name")
        if name is None:
            raise forms.ValidationError("Product name is required")
        if len(name) < 3:
            raise forms.ValidationError("Product name must be at least 3 characters")
        product = Product.objects.filter(name=name, created_by=self.instance.created_by)
        if product.exists():
            raise forms.ValidationError("Product name is already taken")
        return name

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


class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        exclude = ["created_by", "created_at"]
        fields = ["code", "percentage", "expiry_date"]

        widgets = {
            "code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Coupon Code"}
            ),
            "percentage": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Coupon Percentage"}
            ),
            "expiry_date": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Coupon Expiry Date"}
            ),
        }

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code is None:
            raise forms.ValidationError("Coupon code is required")
        if len(code) < 3:
            raise forms.ValidationError("Coupon code must be at least 3 characters")
        return code

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)


class UseCouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = ["code"]

        widgets = {
            "code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Coupon Code"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(UseCouponForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["code"].label = "Coupon"


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["comment"]

        widgets = {
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Comment"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["comment"].label = "Comment"

class ProductReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["comment"]

        widgets = {
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Comment"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ProductReviewForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["comment"].label = "Comment"
