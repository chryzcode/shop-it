# Generated by Django 4.0.6 on 2022-08-06 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0016_alter_wallet_transanction_wallet_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wallet_transanction",
            name="store",
        ),
        migrations.RemoveField(
            model_name="wallet_transanction",
            name="wallet",
        ),
        migrations.RemoveField(
            model_name="withdrawal_transanction",
            name="store",
        ),
        migrations.RemoveField(
            model_name="withdrawal_transanction",
            name="wallet",
        ),
        migrations.DeleteModel(
            name="Wallet",
        ),
        migrations.DeleteModel(
            name="Wallet_Transanction",
        ),
        migrations.DeleteModel(
            name="Withdrawal_Transanction",
        ),
    ]
