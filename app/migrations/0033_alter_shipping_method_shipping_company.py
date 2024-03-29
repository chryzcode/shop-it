# Generated by Django 4.1 on 2022-08-25 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0026_alter_shipping_company_email"),
        ("app", "0032_shipping_method_shipping_company"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shipping_method",
            name="shipping_company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="account.shipping_company",
            ),
        ),
    ]
