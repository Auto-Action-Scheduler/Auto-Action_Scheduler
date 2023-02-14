from rest_framework.serializers import ModelSerializer
from .models import Mail, Message, Reminder


class MailSerializer(ModelSerializer):
    class Meta:
        model = Mail
        fields = ('name', 'subject', 'body', 'attachment', 'sender-mail', 'receiver_mail', 'schedule_time', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ('name', 'phone_number', 'body', 'sender', 'schedule_time', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }


class ReminderSerializer(ModelSerializer):
    class Meta:
        model = Reminder
        fields = ('email', 'text', 'schedule_time', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }
