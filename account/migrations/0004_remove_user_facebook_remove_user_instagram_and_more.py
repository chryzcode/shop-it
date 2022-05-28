# Generated by Django 4.0.3 on 2022-05-22 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_store_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='facebook',
        ),
        migrations.RemoveField(
            model_name='user',
            name='instagram',
        ),
        migrations.RemoveField(
            model_name='user',
            name='twitter',
        ),
        migrations.AddField(
            model_name='store',
            name='facebook',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='store',
            name='instagram',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='store',
            name='twitter',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]