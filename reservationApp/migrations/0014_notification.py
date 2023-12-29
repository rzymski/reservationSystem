# Generated by Django 4.2.6 on 2023-12-29 23:37

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reservationApp', '0013_alter_availablebookingdate_breakbetweenintervals'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=300)),
                ('hasBeenSeen', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 12, 29, 23, 37, 32, 229790))),
                ('availableBookingDate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reservationApp.availablebookingdate')),
                ('fromUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_from', to=settings.AUTH_USER_MODEL)),
                ('reservation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reservationApp.reservation')),
                ('toUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
