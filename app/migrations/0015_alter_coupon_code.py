# Generated by Django 4.0.4 on 2022-06-03 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_product_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
