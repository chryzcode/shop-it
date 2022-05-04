# Generated by Django 4.0.3 on 2022-05-04 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_store_staff_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='store_creator',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='store_staff',
            name='store',
            field=models.CharField(choices=[('code store', 'code store')], max_length=100),
        ),
    ]
