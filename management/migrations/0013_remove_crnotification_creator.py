# Generated by Django 5.0.8 on 2024-08-29 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0012_crnotification_creator_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crnotification',
            name='creator',
        ),
    ]
