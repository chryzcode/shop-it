# Generated by Django 4.0.4 on 2022-06-05 00:30

import ckeditor.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.store')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ProductUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image_1', models.ImageField(upload_to='product-images/')),
                ('image_2', models.ImageField(upload_to='product-images/')),
                ('image_3', models.ImageField(blank=True, null=True, upload_to='product-images/')),
                ('image_4', models.ImageField(blank=True, null=True, upload_to='product-images/')),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0)])),
                ('in_stock', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('availability', models.IntegerField(default=1)),
                ('product_details', ckeditor.fields.RichTextField(blank=True, max_length=300, null=True)),
                ('discount_percentage', models.IntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('currency', models.CharField(max_length=50)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_category', to='app.category')),
                ('product_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_unit', to='app.productunit')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.store')),
                ('wishlist', models.ManyToManyField(blank=True, related_name='wishlist', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Products',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=20, null=True)),
                ('percentage', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expiry_date', models.IntegerField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.store')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
