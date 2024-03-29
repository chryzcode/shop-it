# Generated by Django 4.1 on 2022-08-19 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0019_alter_store_currency"),
    ]

    operations = [
        migrations.AddField(
            model_name="store",
            name="address",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="store",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="account.currency",
            ),
        ),
    ]
