# Generated by Django 4.0.3 on 2022-05-07 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_store_staff_store'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
    ]