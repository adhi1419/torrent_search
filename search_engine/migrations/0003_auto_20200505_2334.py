# Generated by Django 3.0.6 on 2020-05-05 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('search_engine', '0002_auto_20200505_2329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchrecord',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search_engine.Category'),
        ),
        migrations.AlterField(
            model_name='searchrecord',
            name='tracker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search_engine.Tracker'),
        ),
    ]
