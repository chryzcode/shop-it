# Generated by Django 4.0.3 on 2022-06-27 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_payment_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(max_length=20),
        ),
    ]
