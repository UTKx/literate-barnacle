# Generated by Django 3.0 on 2021-01-13 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_discountcode_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountcode',
            name='amount',
            field=models.FloatField(default=0),
        ),
    ]