from django.test import TestCase

from app.models import User, Category, Product

class TestCategoryModel(TestCase):
    def test_category_model(self):
        category = Category.objects.create(name="test there")
        self.assertEqual(category.name, "test there")
        self.assertEqual(category.slug, "test-there")