from dataclasses import field
from django import forms
from django.forms import ModelForm

from .models import *


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


class nonAuthReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["title", "comment", "full_name", "email"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Review Title"}
            ),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Comment"}
            ),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name")
        if name is None:
            raise forms.ValidationError("Field is required")
        return name

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if comment is None:
            raise forms.ValidationError("Field is required")
        if len(comment) <= 5:
            raise forms.ValidationError("Field is requires more than 5 characters")
        return comment

    def __init__(self, *args, **kwargs):
        super(nonAuthReviewForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["comment"].label = "Comment"


class AuthReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["title", "comment"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Title"}
            ),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Comment"}
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if comment is None:
            raise forms.ValidationError("Field is required")
        if len(comment) <= 5:
            raise forms.ValidationError("Field is requires more than 5 characters")
        return comment

    def __init__(self, *args, **kwargs):
        super(AuthReviewForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["comment"].label = "Comment"


class nonAuthProductReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["title", "comment", "full_name", "email"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Title"}
            ),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Comment"}
            ),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name")
        if name is None:
            raise forms.ValidationError("Field is required")
        return name

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if comment is None:
            raise forms.ValidationError("Field is required")
        if len(comment) <= 5:
            raise forms.ValidationError("Field is requires more than 5 characters")
        return comment

    def __init__(self, *args, **kwargs):
        super(nonAuthProductReviewForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["comment"].label = "Comment"


class authProductReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["title", "comment"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Title"}
            ),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Comment"}
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if comment is None:
            raise forms.ValidationError("Field is required")
        if len(comment) <= 5:
            raise forms.ValidationError("Field is requires more than 5 characters")
        return comment

    def __init__(self, *args, **kwargs):
        super(authProductReviewForm, self).__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields["comment"].label = "Comment"


class ShippingMethodForm(ModelForm):
    class Meta:
        model = Shipping_Method
        fields = ["location", "price"]

        widgets = {
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Location Coverage"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Price"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(ShippingMethodForm, self).__init__(*args, **kwargs)


class CompanyAuthReviewForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Title"})
    )
    review = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Comment"})
    )

    def clean_review(self):
        review = self.cleaned_data.get("review")
        if review is None:
            raise forms.ValidationError("Field is required")
        if len(review) <= 5:
            raise forms.ValidationError("Field is requires more than 5 characters")
        return review

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title is None:
            raise forms.ValidationError("Field is required")
        return title


class CompanyNonAuthReviewForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Title"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    review = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Comment"})
    )

    def clean_review(self):
        review = self.cleaned_data.get("review")
        if review is None:
            raise forms.ValidationError("Field is required")
        if len(review) <= 5:
            raise forms.ValidationError("Field is requires more than 5 characters")
        return review

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title is None:
            raise forms.ValidationError("Field is required")
        return title

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email is None:
            raise forms.ValidationError("Field is required")
        if "@" not in email:
            raise forms.ValidationError("Invalid email")
        return email

class NewsletterForm(ModelForm):
    class Meta:
        model = Newsletter
        fields = ["title", "body"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Title"}
            ),
            "body": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Body"}
            ),
        }

        def clean_body(self):
            body = self.cleaned_data.get("body")
            if body is None:
                raise forms.ValidationError("Field is required")
            if body >= 5:
                raise forms.ValidationError("Field is requires more than 5 characters")
            return body

        def clean_title(self):
            title = self.cleaned_data.get("title")
            if title is None:
                raise forms.ValidationError("Field is required")
            if title >= 5:
                raise forms.ValidationError("Field is requires more than 5 characters")
            return title
    
    def __init__(self, *args, **kwargs):
        super(NewsletterForm, self).__init__(*args, **kwargs)
    