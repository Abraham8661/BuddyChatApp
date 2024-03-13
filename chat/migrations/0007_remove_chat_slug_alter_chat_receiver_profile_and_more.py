# Generated by Django 5.0.2 on 2024-03-02 16:11

import django.db.models.deletion
import shortuuid.django_fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddysocial', '0021_delete_bookmark'),
        ('chat', '0006_chat_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='slug',
        ),
        migrations.AlterField(
            model_name='chat',
            name='receiver_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiver_profile', to='buddysocial.profile'),
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', shortuuid.django_fields.ShortUUIDField(alphabet='1234567890+=&?abcdefghijklmnopqrstuvwxyz', length=30, max_length=35, prefix='', unique=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('receiver_user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiver_user', to=settings.AUTH_USER_MODEL)),
                ('sender_user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='room',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.chatroom'),
        ),
    ]
