# Generated by Django 5.0.2 on 2024-02-26 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddysocial', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp_manager',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]