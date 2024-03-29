# Generated by Django 4.1 on 2022-08-25 09:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0022_alter_bank_info_account_name_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Shipping_Company",
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
                ("name", models.CharField(max_length=300)),
                ("account_name", models.CharField(max_length=300)),
                ("bank_code", models.CharField(max_length=10)),
                ("bank_name", models.CharField(max_length=100)),
                ("account_number", models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name="store",
            name="shipping_company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="account.shipping_company",
            ),
        ),
    ]
