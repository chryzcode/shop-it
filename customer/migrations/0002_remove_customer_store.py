# Generated by Django 4.0.4 on 2022-06-04 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='store',
        ),
    ]
