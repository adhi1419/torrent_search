# Generated by Django 3.0.6 on 2020-05-07 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search_engine', '0009_searchrecord_desc_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='tracker',
            options={'ordering': ['title']},
        ),
    ]
