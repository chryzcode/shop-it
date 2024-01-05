# Generated by Django 4.1.1 on 2024-01-05 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_alter_shipping_company_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipping_Method',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200)),
                ('price', models.PositiveIntegerField(default=0)),
                ('location', models.CharField(max_length=200)),
                ('flutterwave_fund', models.PositiveIntegerField(default=0)),
                ('shopit_fund', models.PositiveIntegerField(default=0)),
                ('total_funds', models.PositiveIntegerField(default=0)),
                ('country_code', models.CharField(blank=True, max_length=10, null=True)),
                ('state_code', models.CharField(blank=True, max_length=10, null=True)),
                ('shipping_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.shipping_company')),
            ],
        ),
    ]
