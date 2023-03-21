import json
import uuid

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from phonenumber_field.phonenumber import to_python
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.exceptions import ValidationError

from AutoActionScheduler.celery import app
from .calendarapi import sync_event
from .models import Action
from .tasks import perform_task, send_sms


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)


class CustomPhoneNumberField(PhoneNumberField):
    def to_internal_value(self, data):
        phone_number = to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])
        return phone_number.as_e164


class ActionField(serializers.Serializer):
    TYPES = (
        ("Mail", "Mail"),
        ("SMS", "SMS"),
        ("Reminder", "Reminder")
    )
    action_type = serializers.ChoiceField(choices=TYPES)
    description = serializers.CharField()
    email = serializers.EmailField(required=False)
    receiver_mail = serializers.ListField(child=serializers.EmailField(), required=False)
    phone_number = serializers.ListField(child=CustomPhoneNumberField(), required=False)
    subject = serializers.CharField(max_length=250, required=False)
    sms_sender = serializers.CharField(max_length=250, required=False)
    attachment = serializers.CharField(required=False)
    is_executed = serializers.BooleanField(default=False)
    auth_url = serializers.CharField(required=False)
    uid = serializers.CharField(required=False)

    def validate(self, attrs):
        action_type = attrs.get('action_type')
        subject = attrs.get('subject')
        receiver_mail = attrs.get('receiver_mail')
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        sms_sender = attrs.get('sms_sender')
        attachment = attrs.get('attachment')

        if action_type == "Mail":
            if not subject:
                raise serializers.ValidationError('Mail subject must be provided.')
            elif not receiver_mail:
                raise serializers.ValidationError('Receiver mail must be provided.')
            elif not email:
                raise serializers.ValidationError('Email must be provided.')
            elif phone_number:
                raise serializers.ValidationError('Phone number is not needed')
            elif sms_sender:
                raise serializers.ValidationError('sms sender is not needed')
        elif action_type == "SMS":
            if subject:
                raise serializers.ValidationError('Subject is not needed.')
            elif receiver_mail:
                raise serializers.ValidationError('Receiver mail is not needed.')
            elif attachment:
                raise serializers.ValidationError('Attachment is not needed.')
            elif email:
                raise serializers.ValidationError('Email is not needed.')
            elif not phone_number:
                raise serializers.ValidationError('Phone number must be provided')
            elif not sms_sender:
                raise serializers.ValidationError('sms sender must be provided')
        elif action_type == "Reminder":
            if subject:
                raise serializers.ValidationError('Mail subject is not needed.')
            elif receiver_mail:
                raise serializers.ValidationError('Receiver mail is not needed.')
            elif attachment:
                raise serializers.ValidationError('Attachment is not needed.')
            elif not email:
                raise serializers.ValidationError('Email must be provided.')
            elif phone_number:
                raise serializers.ValidationError('Phone number is not needed')
            elif sms_sender:
                raise serializers.ValidationError('sms sender is not needed')
        return attrs


class ActionSerializer(serializers.ModelSerializer):
    actions = serializers.ListField(child=ActionField())

    class Meta:
        model = Action
        fields = ('id', 'name', 'created_by', 'schedule_time', 'actions', 'task_id', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate_schedule_time(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError('Schedule time must be in future.')
        return value

    def validate_actions(self, value):
        if not value:
            raise serializers.ValidationError('Actions must be provided')
        return value

    # def validate(self, attrs):
    #     name = attrs.get('name')
    #     schedule_time = attrs.get('schedule_time')
    #     actions = attrs.get('actions')
    #
    #     if Action.active_objects.filter(name=name, schedule_time=schedule_time, actions=actions).exists():
    #         raise serializers.ValidationError("Data already exist.")
    #
    #     return attrs


class CancelActionSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()


class CreateReminderSerializer(serializers.Serializer):
    auth_url = serializers.URLField()
    obj_id = serializers.IntegerField()
    uid = serializers.UUIDField()


class AttachmentSerializer(serializers.Serializer):
    attachment = serializers.FileField()

    def validate_attachment(self, value):
        size_limit = 1 * 1024 * 1024
        if value and value.size > size_limit:
            raise serializers.ValidationError('Attachment must not  greater than 1MB')


class ActionRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    actions = serializers.ListField(child=ActionField())

    class Meta:
        model = Action
        fields = ('id', 'name', 'created_by', 'schedule_time', 'actions', 'task_id', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate_schedule_time(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Schedule time must be in future.")
        return value

    def validate_actions(self, value):
        if not value:
            raise serializers.ValidationError('Actions must be provided')
        return value

    def update(self, instance, validated_data):

        update = super().update(instance, validated_data)
        if update.actions:
            app.control.revoke(update.task_id, terminate=True)
            for action in update.actions:
                action['is_executed'] = False
                if action['action_type'] == 'Reminder':
                    action['uid'] = json.dumps(str(uuid.uuid4())).strip('"')
                    auth = sync_event()
                    action['auth_url'] = auth
            update.save()
            task = perform_task.apply_async((update.pk,), eta=update.schedule_time)
            update.task_id = task.id
            update.save()

        return update

# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = ('id', 'name', 'phone_number', 'description', 'sender', 'schedule_time', 'timestamp')
#         extra_kwargs = {
#             'timestamp': {'read_only': True}
#         }
#
#     def validate(self, attrs):
#         schedule_time = attrs.get('schedule_time')
#         phone_number = attrs.get('phone_number')
#
#         if not phone_number[0] == "+":
#             raise serializers.ValidationError("Phone number format should be like +23470XXXXXX")
#
#         if schedule_time and schedule_time <= timezone.now():
#             raise serializers.ValidationError("Schedule time must be in future.")
#
#         return attrs
#
#
# class ReminderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Reminder
#         fields = ('id', 'name', 'email', 'description', 'schedule_time', 'timestamp')
#         extra_kwargs = {
#             'timestamp': {'read_only': True}
#         }
#
#     def validate(self, attrs):
#         schedule_time = attrs.get('schedule_time')
#
#         if schedule_time and schedule_time <= timezone.now():
#             raise serializers.ValidationError("Schedule time must be in future.")
#
#         return attrs
