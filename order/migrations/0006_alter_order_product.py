# Generated by Django 4.0.4 on 2022-06-03 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_coupon_code'),
        ('order', '0005_alter_order_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='product',
            field=models.ManyToManyField(to='app.product'),
        ),
    ]