# Generated by Django 5.1.6 on 2025-03-20 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_profile_profile_pk_profile_profile_pk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='images',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='themes',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Themes'),
        ),
    ]
