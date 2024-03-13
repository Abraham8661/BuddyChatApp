# Generated by Django 5.0.2 on 2024-02-29 13:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddysocial', '0008_story_number_of_bookmarks_bookmarkcategory_bookmark'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookmark',
            name='category',
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='BookmarkCategory',
        ),
    ]
