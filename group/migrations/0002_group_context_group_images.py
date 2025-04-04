# Generated by Django 5.1.6 on 2025-03-11 15:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='context',
            field=models.CharField(default=django.utils.timezone.now, max_length=255, verbose_name='Context'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='images',
            field=models.ImageField(blank=True, null=True, upload_to='review/', verbose_name='Images'),
        ),
    ]
