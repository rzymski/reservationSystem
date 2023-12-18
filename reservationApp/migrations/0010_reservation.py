# Generated by Django 4.2.6 on 2023-12-16 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reservationApp', '0009_alter_userprofile_sex'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('isAccepted', models.BooleanField(default=False)),
                ('availableBookingDate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservationApp.availablebookingdate')),
                ('bookingPerson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]