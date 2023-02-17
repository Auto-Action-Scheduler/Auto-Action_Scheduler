from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

# Create your views here.
from .serializers import MailSerializer, MessageSerializer, ReminderSerializer
from .models import Mail, Message, Reminder
from utils.json_renderer import CustomRenderer


class MailCreateListAPIView(ListCreateAPIView):
    serializer_class = MailSerializer
    queryset = Mail.active_objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    renderer_classes = (CustomRenderer,)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                data = serializer.save()
                if data.schedule_time <= timezone.now():
                    send_mail(from_email=data.sender_mail, subject=data.subject, message=data.description,
                              recipient_list=[data.receiver_mail])
                    data.is_executed = True
                    data.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(e)


class MailRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MailSerializer
    queryset = Mail.active_objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    renderer_classes = (CustomRenderer,)

    def delete(self, request, *args, **kwargs):
        mail_id = self.kwargs.get('pk')
        try:
            mail = Mail.objects.get(id=mail_id)
            mail.is_deleted = not mail.is_deleted
            mail.save()
            if mail.is_deleted:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Mail.DoesNotExist:
            raise ValidationError('Question does not exist.')


class MessageCreateListAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer
    queryset = Message.active_objects.all()
    renderer_classes = (CustomRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    queryset = Message.active_objects.all()
    renderer_classes = (CustomRenderer,)

    def delete(self, request, *args, **kwargs):
        message_id = self.kwargs.get('pk')
        try:
            sms = Message.objects.get(id=message_id)
            sms.is_deleted = not sms.is_deleted
            sms.save()
            if sms.is_deleted:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            raise ValidationError('Question does not exist.')


class ReminderCreateListAPIView(ListCreateAPIView):
    serializer_class = ReminderSerializer
    queryset = Reminder.active_objects.all()
    renderer_classes = (CustomRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReminderRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReminderSerializer
    queryset = Reminder.active_objects.all()
    renderer_classes = (CustomRenderer,)

    def delete(self, request, *args, **kwargs):
        reminder_id = self.kwargs.get('pk')
        try:
            reminder = Reminder.objects.get(id=reminder_id)
            reminder.is_deleted = not reminder.is_deleted
            reminder.save()
            if reminder.is_deleted:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Reminder.DoesNotExist:
            raise ValidationError('Question does not exist.')
