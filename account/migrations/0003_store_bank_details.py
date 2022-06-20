# Generated by Django 4.0.4 on 2022-06-13 18:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_alter_bank_info_currency_alter_store_currency"),
    ]

    operations = [
        migrations.CreateModel(
            name="store_bank_details",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bank_name", models.CharField(max_length=100)),
                ("account_number", models.CharField(max_length=10)),
                ("account_name", models.CharField(max_length=100)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_bank_details",
                        to="account.store",
                    ),
                ),
            ],
        ),
    ]
