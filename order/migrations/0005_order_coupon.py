# Generated by Django 4.0.4 on 2022-06-07 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_date_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]