# Generated by Django 4.1.1 on 2022-09-13 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0008_alter_payment_use_address"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="wallet_transanction",
            options={"ordering": ("-created",)},
        ),
        migrations.AlterModelOptions(
            name="withdrawal_transanction",
            options={"ordering": ("-created",)},
        ),
    ]
