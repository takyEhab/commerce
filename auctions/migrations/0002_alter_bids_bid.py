# Generated by Django 3.2.8 on 2021-11-03 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='bid',
            field=models.IntegerField(),
        ),
    ]