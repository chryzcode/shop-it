# Generated by Django 4.0.6 on 2022-08-07 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_wallet_withdrawal_transanction_wallet_transanction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='amount',
            field=models.PositiveIntegerField(),
        ),
    ]