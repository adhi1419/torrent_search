# Generated by Django 3.0.6 on 2020-05-06 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_engine', '0007_auto_20200506_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchrecord',
            name='id',
            field=models.IntegerField(default=0, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='searchrecord',
            name='size',
            field=models.BigIntegerField(default=0),
        ),
    ]
