# Generated by Django 4.0.6 on 2022-07-12 12:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_remove_store_staff_user"),
        ("app", "0011_rename_customers_last_7_days_customers_yearly_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="customers_monthly",
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
                ("percentage", models.IntegerField(default=0)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="account.store"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "customers_monthly",
            },
        ),
    ]
