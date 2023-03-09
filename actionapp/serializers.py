from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from AutoActionScheduler.celery import app
from .calendarapi import sync_event
from .models import Action
from .tasks import send_email, send_sms


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)


class ActionSerializer(serializers.ModelSerializer):
    phone_number = serializers.ListField(child=serializers.CharField(), max_length=50, required=False)
    receiver_mail = serializers.ListField(child=serializers.EmailField(), required=False)

    class Meta:
        model = Action
        fields = ('id', 'name', 'created_by', 'subject', 'action_type', 'description', 'attachment', 'receiver_mail',
                  'schedule_time',
                  'email', 'phone_number', 'sms_sender', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate_schedule_time(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Schedule time must be in future.")
        return value

    def validate_attachment(self, value):
        size_limit = 1 * 1024 * 1024

        if value and value.size > size_limit:
            raise serializers.ValidationError('Attachment size must not greater than 1MB')

        return value

    def validate(self, attrs):
        action_type = attrs.get('action_type')
        subject = attrs.get('subject')
        receiver_mail = attrs.get('receiver_mail')
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        sms_sender = attrs.get('sms_sender')
        name = attrs.get('name')
        description = attrs.get('description')
        schedule_time = attrs.get('schedule_time')
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
            elif phone_number:
                for num in phone_number:
                    if num[0] != "+":
                        raise serializers.ValidationError('Phone number format should be like +23470XXXXXX')
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

        if Action.active_objects.filter(name=name, description=description, schedule_time=schedule_time,
                                        action_type=action_type,
                                        subject=subject, receiver_mail=receiver_mail, email=email).exists():
            raise serializers.ValidationError("Data already exist.")

        if Action.active_objects.filter(name=name, description=description, schedule_time=schedule_time,
                                        action_type=action_type, email=email).exists():
            raise serializers.ValidationError("Data already exist.")

        if Action.active_objects.filter(name=name, description=description, schedule_time=schedule_time,
                                        action_type=action_type, phone_number=phone_number,
                                        sms_sender=sms_sender).exists():
            raise serializers.ValidationError("Data already exist.")

        return attrs

    def to_representation(self, instance):
        if instance.action_type == "Mail":
            if not instance.attachment:
                return {
                    'id': instance.id,
                    'name': instance.name,
                    'action_type': instance.action_type,
                    'description': instance.description,
                    'created_by': instance.created_by.id,
                    'schedule_time': instance.schedule_time,
                    'timestamp': instance.timestamp,
                    'subject': instance.subject,
                    'email': instance.email,
                    'receiver_mail': instance.receiver_mail,
                    'task_id': instance.task_id
                }
            elif instance.attachment:
                return {
                    'id': instance.id,
                    'name': instance.name,
                    'action_type': instance.action_type,
                    'description': instance.description,
                    'cerated_by': instance.created_by.id,
                    'schedule_time': instance.schedule_time,
                    'timestamp': instance.timestamp,
                    'subject': instance.subject,
                    'email': instance.email,
                    'receiver_mail': instance.receiver_mail,
                    'task_id': instance.task_id,
                    'attachment': instance.attachment.url
                }
        elif instance.action_type == "SMS":
            return {
                'id': instance.id,
                'name': instance.name,
                'action_type': instance.action_type,
                'description': instance.description,
                'created_by': instance.created_by.id,
                'schedule_time': instance.schedule_time,
                'timestamp': instance.timestamp,
                'phone_number': instance.phone_number,
                'sms_sender': instance.sms_sender,
                'task_id': instance.task_id
            }
        elif instance.action_type == "Reminder":
            return {
                'id': instance.id,
                'name': instance.name,
                'action_type': instance.action_type,
                'description': instance.description,
                'created_by': instance.created_by.id,
                'schedule_time': instance.schedule_time,
                'timestamp': instance.timestamp,
                'email': instance.email
            }


class CancelActionSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()


class CreateReminderSerializer(serializers.Serializer):
    auth_url = serializers.URLField()
    user_id = serializers.IntegerField()
    obj_id = serializers.IntegerField()


class ActionRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    phone_number = serializers.ListField(child=serializers.CharField(), max_length=50, required=False)
    receiver_mail = serializers.ListField(child=serializers.EmailField(), required=False)

    class Meta:
        model = Action
        fields = ('id', 'name', 'created_by', 'subject', 'action_type', 'description', 'attachment', 'receiver_mail',
                  'schedule_time',
                  'email', 'phone_number', 'sms_sender', 'timestamp')
        extra_kwargs = {
            'timestamp': {'read_only': True}
        }

    def validate_schedule_time(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Schedule time must be in future.")
        return value

    def update(self, instance, validated_data):
        action_type = validated_data.get('action_type')
        subject = validated_data.get('subject')
        receiver_mail = validated_data.get('receiver_mail')
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        sms_sender = validated_data.get('sms_sender')
        attachment = validated_data.get('attachment')
        size_limit = 1 * 1024 * 1024

        if action_type == "Mail":
            if instance.action_type == "Reminder" or instance.action_type == "SMS":
                raise serializers.ValidationError("You can't swap the action type.")
            elif not subject:
                raise serializers.ValidationError('Mail subject must be provided.')
            elif not receiver_mail:
                raise serializers.ValidationError('Receiver mail must be provided.')
            elif not email:
                raise serializers.ValidationError('Email must be provided.')
            elif phone_number:
                raise serializers.ValidationError('Phone number is not needed')
            elif sms_sender:
                raise serializers.ValidationError('sms sender is not needed')
            elif attachment and attachment.size > size_limit:
                raise serializers.ValidationError('Attachment size must not greater than 1MB')

        if action_type == "SMS":
            if instance.action_type == "Reminder" or instance.action_type == "Mail":
                raise serializers.ValidationError("You can't swap the action type.")
            elif subject:
                raise serializers.ValidationError('Subject is not needed.')
            elif receiver_mail:
                raise serializers.ValidationError('Receiver mail is not needed.')
            elif attachment:
                raise serializers.ValidationError('Attachment is not needed.')
            elif email:
                raise serializers.ValidationError('Email is not needed.')
            elif not phone_number:
                raise serializers.ValidationError('Phone number must be provided')
            elif phone_number:
                for num in phone_number:
                    if num[0] != "+":
                        raise serializers.ValidationError('Phone number format should be like +23470XXXXXX')
            elif not sms_sender:
                raise serializers.ValidationError('sms sender must be provided')

        if action_type == "Reminder":
            if instance.action_type == "Mail" or instance.action_type == "SMS":
                raise serializers.ValidationError("You can't swap the action type.")
            elif subject:
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

        update = super().update(instance, validated_data)

        if update.action_type == 'Mail':
            if update.schedule_time.date() == timezone.localtime().date():
                app.control.revoke(update.task_id, terminate=True)
                update.is_executed = False
                update.save()
                task = send_email.apply_async((update.pk,), eta=update.schedule_time)
                update.task_id = task.id
                update.save()
                return update
            elif update.schedule_time.date() > timezone.localtime().date():
                app.control.revoke(update.task_id, terminate=True)
                update.is_executed = False
                update.save()
                task = send_email.apply_async((update.pk,), eta=update.schedule_time)
                update.task_id = task.id
                update.save()
                return update
        elif update.action_type == 'SMS':
            if update.schedule_time.date() == timezone.localtime().date():
                app.control.revoke(update.task_id, terminate=True)
                update.is_executed = False
                update.save()
                task = send_sms.apply_async((update.pk,), eta=update.schedule_time)
                update.task_id = task.id
                update.save()
                return update
            elif update.schedule_time.date() > timezone.localtime().date():
                app.control.revoke(update.task_id, terminate=True)
                update.is_executed = False
                update.save()
                task = send_sms.apply_async((update.pk,), eta=update.schedule_time)
                update.task_id = task.id
                update.save()
                return update
        return update

    def to_representation(self, instance):
        if instance.action_type == "Mail":
            if not instance.attachment:
                return {
                    'id': instance.id,
                    'name': instance.name,
                    'action_type': instance.action_type,
                    'description': instance.description,
                    'created_by': instance.created_by.id,
                    'schedule_time': instance.schedule_time,
                    'timestamp': instance.timestamp,
                    'subject': instance.subject,
                    'email': instance.email,
                    'receiver_mail': instance.receiver_mail,
                    'task_id': instance.task_id
                }
            elif instance.attachment:
                return {
                    'id': instance.id,
                    'name': instance.name,
                    'action_type': instance.action_type,
                    'description': instance.description,
                    'cerated_by': instance.created_by.id,
                    'schedule_time': instance.schedule_time,
                    'timestamp': instance.timestamp,
                    'subject': instance.subject,
                    'email': instance.email,
                    'receiver_mail': instance.receiver_mail,
                    'task_id': instance.task_id,
                    'attachment': instance.attachment.url
                }
        elif instance.action_type == "SMS":
            return {
                'id': instance.id,
                'name': instance.name,
                'action_type': instance.action_type,
                'description': instance.description,
                'created_by': instance.created_by.id,
                'schedule_time': instance.schedule_time,
                'timestamp': instance.timestamp,
                'phone_number': instance.phone_number,
                'sms_sender': instance.sms_sender,
                'task_id': instance.task_id
            }
        elif instance.action_type == "Reminder":
            return {
                'id': instance.id,
                'name': instance.name,
                'action_type': instance.action_type,
                'description': instance.description,
                'created_by': instance.created_by.id,
                'schedule_time': instance.schedule_time,
                'timestamp': instance.timestamp,
                'email': instance.email
            }

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
