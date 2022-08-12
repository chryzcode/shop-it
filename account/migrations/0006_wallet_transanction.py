# Generated by Django 4.0.6 on 2022-08-04 19:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0005_wallet"),
    ]

    operations = [
        migrations.CreateModel(
            name="Wallet_Transanction",
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
                ("amount", models.PositiveIntegerField(default=0)),
                ("account", models.CharField(max_length=20)),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.currency",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="account.store"
                    ),
                ),
            ],
        ),
    ]
