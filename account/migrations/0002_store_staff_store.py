# Generated by Django 4.0.3 on 2022-05-06 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store_staff',
            name='store',
            field=models.CharField(choices=[], default='hello', max_length=150),
        ),
    ]
