# Generated by Django 4.2.6 on 2023-12-30 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservationApp', '0016_remove_notification_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='availablebookingdate',
            name='isDeleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notification',
            name='isDeleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reservation',
            name='isDeleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
