# Generated by Django 4.0.6 on 2022-08-08 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0004_alter_wallet_amount"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="payment",
            name="city",
        ),
    ]
