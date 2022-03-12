import datetime
from itertools import product

from django.test import TestCase
from django.utils.text import slugify

from app.models import Category, Product, ProductUnit, User


class TestCategoryModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            full_name="Test User Full Name",
            avatar="avatar.jpg",
            email="testuser@gmail.com",
            password="testuserpassword",
        )

        self.category = Category.objects.create(
            name="Test Category",
            created_by=self.user,
        )

        self.product_unit = ProductUnit.objects.create(name="pc")

        self.product = Product.objects.create(
            category=self.category,
            created_by=self.user,
            name="Test Product",
            description="Test Product Description",
            image_1="image_1.jpg",
            image_2="image_2.jpg",
            image_3="image_3.jpg",
            image_4="image_4.jpg",
            price=1000.00,
            in_stock=True,
            product_unit=self.product_unit,
        )

    def test_category_model(self):
        self.assertEqual(self.category.created_by, self.user)
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.slug, slugify(self.category.name))

    def test_product_model(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.slug, slugify(self.product.name))
        self.assertEqual(self.product.description, "Test Product Description")
        self.assertEqual(self.product.image_1, "image_1.jpg")
        self.assertEqual(self.product.image_2, "image_2.jpg")
        self.assertEqual(self.product.image_3, "image_3.jpg")
        self.assertEqual(self.product.image_4, "image_4.jpg")
        self.assertEqual(self.product.price, 1000.00)

    def test_user_model(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.full_name, "Test User Full Name")
        self.assertEqual(self.user.email, "testuser@gmail.com")
        self.assertEqual(self.user.avatar, "avatar.jpg")
        self.assertEqual(self.user.slugified_store_name, slugify(self.user.store_name))
        self.assertEqual(self.user.check_password("testuserpassword"), True)
