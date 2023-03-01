from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView)
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from AutoActionScheduler.celery import app
from utils.outbox import send_sms
from .calendarapi import sync_event
# Create your views here.
from .serializers import ActionSerializer, CancelActionSerializer
from .models import Action
from utils.json_renderer import CustomRenderer
from .tasks import sync_reminder, run_send_mail, send_email, send_sms


class ActionCreateListAPIView(ListCreateAPIView):
    serializer_class = ActionSerializer
    queryset = Action.active_objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            now = timezone.localtime()
            if data.action_type == "Mail":
                if data.schedule_time.date() == now.date():
                    task = send_email.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
                elif data.schedule_time.date() > now.date():
                    task = send_email.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
            elif data.action_type == "SMS":
                if data.schedule_time.date() == now.date():
                    task = send_sms.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
                elif data.schedule_time.date() > now.date():
                    task = send_sms.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
            elif data.action_type == "Reminder":
                sync_event(request, name=data.name, description=data.description, schedule_time=data.schedule_time)
                # task = sync_reminder.delay(request, name=data.name, description=data.description, schedule_time=data.schedule_time)
                return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ActionSerializer
    queryset = Action.active_objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid():
            data = serializer.save()
            now = timezone.localtime()
            if data.action_type == "Mail":
                if data.schedule_time.date() == now.date():
                    task = send_email.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
                elif data.schedule_time.date() > now.date():
                    task = send_email.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
            elif data.action_type == "SMS":
                if data.schedule_time.date() == now.date():
                    task = send_sms.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
                elif data.schedule_time.date() > now.date():
                    task = send_sms.apply_async((data.pk,), eta=data.schedule_time)
                    return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)
            elif data.action_type == "Reminder":
                task = sync_reminder.delay(name=data.name, description=data.description,
                                           schedule_time=data.schedule_time)
                return Response({'data': serializer.data, 'task_id': task.id}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        mail_id = self.kwargs.get('pk')
        try:
            mail = Action.objects.get(id=mail_id)
            mail.is_deleted = not mail.is_deleted
            mail.save()
            if mail.is_deleted:
                return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
            return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
        except Action.DoesNotExist:
            raise ValidationError('Question does not exist.')


class CancelActionAPIView(UpdateAPIView):
    serializer_class = CancelActionSerializer
    queryset = Action.active_objects.all()
    renderer_classes = (CustomRenderer,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            id = serializer.data['task_id']
            try:
                app.control.revoke(id, terminate=True)
                return Response({'message': 'Canceled Successfully'}, status=status.HTTP_200_OK)
            except:
                raise ValidationError('An error occurred.')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class MessageCreateListAPIView(ListCreateAPIView):
#     serializer_class = MessageSerializer
#     queryset = Message.active_objects.all()
#     renderer_classes = (CustomRenderer,)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.save()
#             # if data.schedule_time <= timezone.now():
#             #     send_sms(data.pk)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class MessageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     serializer_class = MessageSerializer
#     queryset = Message.active_objects.all()
#     renderer_classes = (CustomRenderer,)
#
#     def delete(self, request, *args, **kwargs):
#         message_id = self.kwargs.get('pk')
#         try:
#             sms = Message.objects.get(id=message_id)
#             sms.is_deleted = not sms.is_deleted
#             sms.save()
#             if sms.is_deleted:
#                 return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
#             return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
#         except Message.DoesNotExist:
#             raise ValidationError('Question does not exist.')
#
#
# class ReminderCreateListAPIView(ListCreateAPIView):
#     serializer_class = ReminderSerializer
#     queryset = Reminder.active_objects.all()
#     renderer_classes = (CustomRenderer,)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.save()
#             sync_reminder.delay(name=data.name, description=data.description, schedule_time=data.schedule_time)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ReminderRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     serializer_class = ReminderSerializer
#     queryset = Reminder.active_objects.all()
#     renderer_classes = (CustomRenderer,)
#
#     def delete(self, request, *args, **kwargs):
#         reminder_id = self.kwargs.get('pk')
#         try:
#             reminder = Reminder.objects.get(id=reminder_id)
#             reminder.is_deleted = not reminder.is_deleted
#             reminder.save()
#             if reminder.is_deleted:
#                 return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
#             return Response({"data": "Retrieved Successfully"}, status=status.HTTP_200_OK)
#         except Reminder.DoesNotExist:
#             raise ValidationError('Question does not exist.')
