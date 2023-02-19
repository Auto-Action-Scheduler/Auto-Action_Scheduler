from django.utils import timezone
from rest_framework import serializers
from .models import Mail, Message, Reminder


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ('id', 'name', 'subject', 'description', 'attachment', 'sender_mail', 'receiver_mail', 'schedule_time',
                  'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate(self, attrs):
        schedule_time = attrs.get('schedule_time')
        attachment = attrs.get('attachment')
        size_limit = 1 * 1024 * 1024

        if schedule_time and schedule_time < timezone.now():
            raise serializers.ValidationError("Schedule time must be in future.")

        if attachment and attachment.size > size_limit:
            raise serializers.ValidationError('Attachment size must not greater than 1MB')

        return attrs


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'name', 'phone_number', 'description', 'sender', 'schedule_time', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate(self, attrs):
        schedule_time = attrs.get('schedule_time')

        if schedule_time and schedule_time < timezone.now():
            raise serializers.ValidationError("Schedule time must be in future.")

        return attrs


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ('id', 'name', 'email', 'description', 'schedule_time', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate(self, attrs):
        schedule_time = attrs.get('schedule_time')

        if not schedule_time:
            raise serializers.ValidationError("schedule time must be provided")

        if schedule_time and schedule_time <= timezone.now():
            raise serializers.ValidationError("Schedule time must be in future.")

        return attrs
