# Generated by Django 4.0.6 on 2022-08-04 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0010_remove_wallet_transanction_account_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="withdrawal_transanction",
            name="account_bank",
            field=models.CharField(default="hi", max_length=200),
        ),
    ]
