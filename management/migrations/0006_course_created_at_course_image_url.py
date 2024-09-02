# Generated by Django 5.0.8 on 2024-08-20 12:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_alter_assignment_course_assignmentsubmission'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='course',
            name='image_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
