# Generated by Django 5.1.6 on 2025-04-04 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0007_rename_schdule_month_room_schdule_monthly'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='schdule_monthly',
            new_name='schedule_monthly',
        ),
        migrations.RenameField(
            model_name='room',
            old_name='schdule_weekly',
            new_name='schedule_weekly',
        ),
    ]
