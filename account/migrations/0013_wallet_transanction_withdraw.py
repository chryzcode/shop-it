# Generated by Django 4.0.6 on 2022-08-04 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0012_alter_withdrawal_transanction_account_bank"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallet_transanction",
            name="withdraw",
            field=models.BooleanField(default=False),
        ),
    ]
