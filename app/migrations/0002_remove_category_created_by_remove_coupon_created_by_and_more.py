# Generated by Django 4.0.4 on 2022-06-04 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='product',
            name='store',
        ),
    ]
