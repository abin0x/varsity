# Generated by Django 5.0.8 on 2024-08-19 08:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_notification_teacher_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.assignment'),
        ),
    ]
