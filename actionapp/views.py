from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

# Create your views here.
from .serializers import MailSerializer, MessageSerializer, ReminderSerializer
from .models import Mail, Message, Reminder
from utils.json_renderer import CustomRenderer
from .tasks import send_email


class MailCreateListAPIView(ListCreateAPIView):
    serializer_class = MailSerializer
    queryset = Mail.active_objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    renderer_classes = (CustomRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # print(serializer.data)
            # sender = serializer.data.get('sender_mail')
            # receiver = serializer.data.get('receiver_mail')
            # html_content = serializer.data.get('description')
            # subject = serializer.data.get('subject')
            # send_email(from_email='labisoye@afexnigeria.com', to_emails='yoyedele@afexnigeria.com', subject='Mail Subject', html_content='Mail Body')
            print('Got here')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
