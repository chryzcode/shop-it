from django.forms import ModelForm

from .models import Category, Product


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

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
