# Generated by Django 4.0.3 on 2022-05-11 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_alter_store_store_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='store_staff',
            field=models.BooleanField(default=False),
        ),
    ]