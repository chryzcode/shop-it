# Generated by Django 4.0.4 on 2022-06-04 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_category_created_by_remove_coupon_created_by_and_more'),
        ('order', '0002_remove_order_store'),
        ('customer', '0002_remove_customer_store'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Currency',
        ),
        migrations.RemoveField(
            model_name='shipping_method',
            name='store',
        ),
        migrations.RemoveField(
            model_name='store_staff',
            name='store',
        ),
        migrations.DeleteModel(
            name='Store',
        ),
    ]
