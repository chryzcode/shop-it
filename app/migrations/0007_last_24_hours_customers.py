# Generated by Django 4.0.6 on 2022-07-12 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_remove_store_staff_user'),
        ('app', '0006_last_7_days_customers'),
    ]

    operations = [
        migrations.CreateModel(
            name='last_24_hours_customers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.IntegerField(default=0)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.store')),
            ],
            options={
                'verbose_name_plural': 'last_24_hours_customers',
            },
        ),
    ]
