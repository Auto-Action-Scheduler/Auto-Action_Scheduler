# Generated by Django 4.1.7 on 2023-03-21 08:52

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('actionapp', '0005_alter_action_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='action',
            unique_together={('created_by', 'name', 'schedule_time', 'actions')},
        ),
    ]
