# Generated by Django 4.1 on 2022-08-17 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0017_remove_wallet_transanction_store_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="store",
            name="currency",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="account.currency",
            ),
        ),
    ]