# Generated by Django 3.0.6 on 2020-05-05 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.DurationField()),
                ('tracker', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('size', models.IntegerField(default=0)),
                ('category', models.CharField(max_length=25)),
                ('seeds', models.IntegerField(default=0)),
                ('leechers', models.IntegerField(default=0)),
                ('magnet', models.CharField(max_length=400)),
            ],
        ),
    ]
