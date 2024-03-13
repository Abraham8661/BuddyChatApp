# Generated by Django 5.0.2 on 2024-03-02 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('buddysocial', '0021_delete_bookmark'),
        ('chat', '0004_remove_profile_user_delete_otp_manager_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('receiver_profile', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receier_profile', to='buddysocial.profile')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender', to=settings.AUTH_USER_MODEL)),
                ('sender_profile', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender_profile', to='buddysocial.profile')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]