# Generated by Django 3.0.6 on 2020-05-06 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_engine', '0006_auto_20200506_0139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchrecord',
            name='magnet',
            field=models.CharField(max_length=800),
        ),
    ]
