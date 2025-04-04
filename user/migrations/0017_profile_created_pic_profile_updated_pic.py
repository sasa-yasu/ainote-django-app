# Generated by Django 5.1.6 on 2025-04-05 14:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_alter_profile_mbti'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created_pic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_created_pics', to='user.profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='updated_pic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_updated_pics', to='user.profile'),
        ),
    ]
