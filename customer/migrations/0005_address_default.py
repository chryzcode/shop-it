# Generated by Django 4.0.3 on 2022-05-13 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_alter_customer_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='default',
            field=models.BooleanField(default=False, verbose_name='Default'),
        ),
    ]