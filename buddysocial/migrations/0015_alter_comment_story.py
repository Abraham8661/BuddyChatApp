# Generated by Django 5.0.2 on 2024-03-01 11:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddysocial', '0014_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='story',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buddysocial.story'),
        ),
    ]