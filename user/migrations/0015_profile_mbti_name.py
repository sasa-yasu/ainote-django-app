# Generated by Django 5.1.6 on 2025-04-01 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_alter_profile_mbti'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='mbti_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
