from django.test import Client, TestCase
from django.urls import reverse
import datetime

from app.models import Category, Product, User


class TestViews(TestCase):
    def setUp(self):

        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user",
            full_name="Test User Full Name",
            store_name="Testing Shop",
            avatar="avatar.jpg",
            email="testuser@gmail.com",
            password="testuserpassword",
        )
        self.user.save()

        self.category = Category.objects.create(
            name="Test Category",
            created_by=self.user,
        )

        self.product = Product.objects.create(
            category=self.category,
            created_by=self.user,
            name="Test Product",
            description="Test Product Description",
            price=1000.00,
            in_stock= True,
            is_active=True,
            created= datetime.date.today(),
            updated= datetime.date.today(),
            image_1="image_1.jpg",
            image_2="image_2.jpg",
            image_3="image_3.jpg",
            image_4="image_4.jpg",
        )

    def test_a_user_all_products(self):
        response = self.client.get(
            reverse(
                "app:a_user_all_products",
                kwargs={"slugified_store_name": self.user.slugified_store_name},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/a-user-all-products.html")

 
