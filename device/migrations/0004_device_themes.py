# Generated by Django 5.1.6 on 2025-03-28 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0003_device_likes_device_likes_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='themes',
            field=models.ImageField(blank=True, null=True, upload_to='device', verbose_name='Themes'),
        ),
    ]
