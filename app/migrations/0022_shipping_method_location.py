# Generated by Django 4.1 on 2022-08-19 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0021_alter_shipping_method_country_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shipping_method",
            name="location",
            field=models.CharField(default="hi", max_length=200),
        ),
    ]
