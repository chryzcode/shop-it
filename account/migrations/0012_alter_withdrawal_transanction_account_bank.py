# Generated by Django 4.0.6 on 2022-08-04 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_withdrawal_transanction_account_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawal_transanction',
            name='account_bank',
            field=models.CharField(max_length=200),
        ),
    ]