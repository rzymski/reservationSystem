# Generated by Django 4.2.6 on 2023-12-20 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservationApp', '0012_alter_reservation_availablebookingdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availablebookingdate',
            name='breakBetweenIntervals',
            field=models.IntegerField(default=0),
        ),
    ]
