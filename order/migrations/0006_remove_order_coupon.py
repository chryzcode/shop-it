# Generated by Django 4.0.4 on 2022-06-07 23:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_order_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='coupon',
        ),
    ]
