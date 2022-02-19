from django.http import HttpRequest
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.text import slugify

from app.models import *
from app.views import *
from app.views import a_user_all_products


class TestTemplates(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            full_name="Test User Full Name",
            avatar="avatar.jpg",
            email="testuser@gmail.com",
            password="testuserpassword",
        )

    def test_a_user_all_products(self):
        request = HttpRequest()
        response = a_user_all_products(request, slugify(self.user.username))
        html = response.content.decode("utf8")
        print(html)
        self.assertIn("<title> Shop !t -  - All Products</title>", html)
        self.assertTrue(html.startswith("\n<!DOCTYPE html>\n"))

    def test_view_function(self):
        request = self.factory.get(
            reverse(
                "app:a_user_all_products",
                kwargs={"slugified_username": slugify(self.user.username)},
            )
        )
        response = a_user_all_products(request, slugify(self.user.username))
        html = response.content.decode("utf8")
        print(html)
        self.assertIn("<title> Shop !t -  - All Products</title>", html)
        self.assertTrue(html.startswith("\n<!DOCTYPE html>\n"))
        self.assertTrue(response.status_code, 200)
