# Generated by Django 4.0.3 on 2022-03-03 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]