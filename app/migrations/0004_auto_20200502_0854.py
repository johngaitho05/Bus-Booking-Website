# Generated by Django 2.2.7 on 2020-05-02 05:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_booking_booking_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='booking_time',
            new_name='booking_datetime',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='travelling_time',
            new_name='travelling_datetime',
        ),
    ]
