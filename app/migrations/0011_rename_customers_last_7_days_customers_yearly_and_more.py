# Generated by Django 4.0.6 on 2022-07-12 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_remove_store_staff_user'),
        ('app', '0010_alter_last_30_days_sales_options_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='customers_last_7_days',
            new_name='customers_yearly',
        ),
        migrations.AlterModelOptions(
            name='customers_yearly',
            options={'verbose_name_plural': 'customers_yearly'},
        ),
    ]