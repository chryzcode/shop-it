# Generated by Django 4.0.4 on 2022-06-04 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_remove_store_currency_currency_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='store',
            field=models.ManyToManyField(blank=True, related_name='store_currency', to='account.store'),
        ),
    ]
