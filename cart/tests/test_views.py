from django.test import TestCase, Client
from django.urls import reverse

from app.models import Category, Product, User, ProductUnit


class TestCartView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            full_name="Test User Full Name",
            store_name="Testing Shop",
            avatar="avatar.jpg",
            email="testuser@gmail.com",
            password="testuserpassword",
        )
        
        self.category = Category.objects.create(
            name="Test Category",
            created_by=self.user,
        )

        self.product_unit = ProductUnit.objects.create(
            name= "pc"
        )
        
        self.product = Product.objects.create(
            category=self.category,
            created_by=self.user,
            name="Test Product",
            description="Test Product Description",
            price=20.00,
            in_stock=True,
            image_1="image_1.jpg",
            image_2="image_2.jpg",
            image_3="image_3.jpg",
            image_4="image_4.jpg",
            product_unit = self.product_unit
        )

        self.product = Product.objects.create(
            category=self.category,
            created_by=self.user,
            name="Test Product 2",
            description="Test Product Description",
            price=20.00,
            in_stock=True,
            image_1="image_1.jpg",
            image_2="image_2.jpg",
            image_3="image_3.jpg",
            image_4="image_4.jpg",
            product_unit = self.product_unit
        )

        self.product = Product.objects.create(
            category=self.category,
            created_by=self.user,
            name="Test Product 3",
            description="Test Product Description",
            price=20.00,
            in_stock=True,
            image_1="image_1.jpg",
            image_2="image_2.jpg",
            image_3="image_3.jpg",
            image_4="image_4.jpg",
            product_unit = self.product_unit
        )

        self.client.post(reverse("cart:add_to_cart"), 
        {
            "productid": 1,
            "productqty": 1,
            "action": 'post'
        }, xhr=True)

        self.client.post(reverse("cart:add_to_cart"), 
        {
            "productid": 2,
            "productqty": 2,
            "action": 'post'
        }, xhr=True)

        self.client.post(reverse("cart:add_to_cart"), 
        {
            "productid": 3,
            "productqty": 2,
            "action": 'post'
        }, xhr=True)

    def test_cart_url(self):
        response = self.client.get(reverse('cart:cart_summary'))
        self.assertEqual(response.status_code, 200)

    def test_cart_add(self):
        response = self.client.post(
            reverse('cart:add_to_cart'), {"productid": 3, "productqty": 1, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 4})
        response = self.client.post(
            reverse('cart:add_to_cart'), {"productid": 2, "productqty": 1, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 3})

    def test_cart_update(self):
        response = self.client.post(
            reverse('cart:update_cart'), {"productid": 2, "productqty": 1, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 2, 'subtotal': '40.00'})

    def test_cart_delete(self):
        response = self.client.post(
            reverse('cart:delete_form_cart'), {"productid": 3, "action": "post"}, xhr=True)
        self.assertEqual(response.json(), {'qty': 0, 'subtotal': 0})