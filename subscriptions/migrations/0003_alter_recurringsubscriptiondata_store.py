# Generated by Django 4.0.5 on 2022-07-02 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
        ("subscriptions", "0002_remove_recurringsubscriptiondata_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recurringsubscriptiondata",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="account.store"
            ),
        ),
    ]
