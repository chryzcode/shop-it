# Generated by Django 4.1.1 on 2024-01-05 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_alter_payment_shipping_method'),
        ('app', '0036_alter_product_normal_price'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Shipping_Method',
        ),
    ]
