# Generated by Django 5.1.6 on 2025-03-20 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_profile_images_alter_profile_themes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='images',
            field=models.ImageField(blank=True, null=True, upload_to='user', verbose_name='Images'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='themes',
            field=models.ImageField(blank=True, null=True, upload_to='user', verbose_name='Themes'),
        ),
    ]
