# Generated by Django 5.1.6 on 2025-04-05 14:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0003_notice_published_at_notice_remarks'),
        ('user', '0017_profile_created_pic_profile_updated_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='created_pic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_created_pics', to='user.profile'),
        ),
        migrations.AddField(
            model_name='notice',
            name='updated_pic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notice_updated_pics', to='user.profile'),
        ),
    ]
