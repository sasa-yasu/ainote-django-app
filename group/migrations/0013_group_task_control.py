# Generated by Django 5.1.6 on 2025-04-05 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0012_group_schedule_monthly_group_schedule_weekly'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='task_control',
            field=models.CharField(blank=True, max_length=1028, null=True, verbose_name='Task Control'),
        ),
    ]
