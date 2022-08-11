# Generated by Django 4.0.6 on 2022-08-06 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_remove_wallet_transanction_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet_transanction',
            name='wallet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.wallet'),
        ),
        migrations.AlterField(
            model_name='withdrawal_transanction',
            name='wallet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.wallet'),
        ),
    ]