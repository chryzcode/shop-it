# Generated by Django 4.0.3 on 2022-05-24 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_alter_customer_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='store',
            field=models.CharField(max_length=150),
        ),
    ]