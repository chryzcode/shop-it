# Generated by Django 4.0.6 on 2022-08-06 09:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0013_wallet_transanction_withdraw"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wallet_transanction",
            name="currency",
        ),
        migrations.RemoveField(
            model_name="withdrawal_transanction",
            name="currency",
        ),
        migrations.AddField(
            model_name="wallet_transanction",
            name="wallet",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="account.wallet",
            ),
        ),
        migrations.AddField(
            model_name="withdrawal_transanction",
            name="wallet",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="account.wallet",
            ),
        ),
    ]
