# Generated by Django 4.1.7 on 2023-02-27 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('schedule_time', models.DateTimeField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_executed', models.BooleanField(default=False)),
                ('action_type', models.CharField(choices=[('Mail', 'Mail'), ('SMS', 'SMS'), ('Reminder', 'Reminder')], max_length=150)),
                ('subject', models.CharField(blank=True, max_length=250, null=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='attachment')),
                ('receiver_mail', models.JSONField(blank=True, default=list, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.JSONField(blank=True, default=list, null=True)),
                ('sms_sender', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
