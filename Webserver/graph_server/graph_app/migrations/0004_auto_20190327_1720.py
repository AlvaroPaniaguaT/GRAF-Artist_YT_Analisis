# Generated by Django 2.1.7 on 2019-03-27 17:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_app', '0003_auto_20190327_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphitem',
            name='grade',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)]),
        ),
    ]
