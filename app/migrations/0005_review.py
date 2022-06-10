# Generated by Django 4.0.4 on 2022-06-10 00:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_bank_info_currency_alter_store_currency'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0004_remove_product_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.store')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]