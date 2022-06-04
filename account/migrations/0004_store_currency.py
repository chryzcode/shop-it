# Generated by Django 4.0.4 on 2022-06-04 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_remove_store_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='currency',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.currency'),
        ),
    ]
