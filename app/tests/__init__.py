from django.test import TestCase

from app.models import User, Category, Product

class TestCategoryModel(TestCase):
    def test_category_model(self):
        category = Category.objects.create(name="test", slug="test")
        self.assertEqual(category.name, "test")
        self.assertEqual(category.slug, "test")
        self.assertEqual(str(category), "test")