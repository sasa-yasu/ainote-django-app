# Generated by Django 5.1.6 on 2025-03-28 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0003_room_likes_room_likes_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='themes',
            field=models.ImageField(blank=True, null=True, upload_to='room', verbose_name='Themes'),
        ),
    ]
