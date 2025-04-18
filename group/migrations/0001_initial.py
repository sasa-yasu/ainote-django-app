# Generated by Django 5.1.6 on 2025-04-19 16:22

import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('images', models.ImageField(blank=True, null=True, upload_to='group', verbose_name='Images')),
                ('themes', models.ImageField(blank=True, null=True, upload_to='group', verbose_name='Themes')),
                ('category_choice', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('sports', '⚽スポーツ🏃\u200d♀️'), ('walking', '🚶\u200d♂️歩活（ウォーキング）🌳'), ('bbq', '🍖バーベキュー🔥'), ('music', '🎵音楽・演奏🎸'), ('study', '📚勉強会・学習🧠'), ('hobby', '🎨趣味・創作✂️'), ('childcare', '🍼子育てサークル👶'), ('volunteer', '🤝ボランティア👐'), ('intergenerational', '👨\u200d👩\u200d👧\u200d👦世代交流🕊️'), ('community', '🏘️地域活動👫'), ('other', '🧩その他🗂️')], max_length=200, null=True, verbose_name='Category Choice')),
                ('context', models.TextField(blank=True, null=True, verbose_name='Context')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='Remarks')),
                ('schedule_monthly', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Schedule Monthly')),
                ('schedule_weekly', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Schedule Weekly')),
                ('task_control', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Task Control')),
                ('likes', models.IntegerField(blank=True, default=0, null=True)),
                ('likes_record', models.TextField(blank=True, default='|', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
        ),
    ]
