from importlib import import_module

from django.conf import settings
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
            store_name="Testing Shop",
            avatar="avatar.jpg",
            email="testuser@gmail.com",
            password="testuserpassword",
        )

    def test_a_user_all_products(self):
        request = HttpRequest()
        response = a_user_all_products(request, slugify(self.user.store_name))
        html = response.content.decode("utf8")
        print(html)
        self.assertTrue(response.status_code, 200)

    # def test_a_user_all_products(self):
    #     request = self.factory.get(
    #         reverse(
    #             "app:a_user_all_products",
    #             kwargs={"slugified_store_name": slugify(self.user.store_name)},
    #         )
    #     )
    #     response = a_user_all_products(request, slugify(self.user.store_name))
    #     html = response.content.decode("utf8")
    #     print(html)
    #     self.assertTrue(response.status_code, 200)

    def test_homepage(self):
        request = self.factory.get(reverse("app:home_page"))
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        response = home_page(request)
        self.assertTrue(response.status_code, 200)
