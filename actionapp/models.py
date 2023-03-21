import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_deleted=False)


class DeleteManager(models.Manager):
    def get_queryset(self):
        return super(DeleteManager, self).get_queryset().filter(is_deleted=True)


class Action(models.Model):
    TYPES = (
        ("Mail", "Mail"),
        ("SMS", "SMS"),
        ("Reminder", "Reminder")
    )

    name = models.CharField(max_length=200)
    schedule_time = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    actions = models.JSONField(default=list)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=200, null=True, blank=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    class Meta:
        unique_together = ('created_by', 'name', 'schedule_time')

    def __str__(self):
        return self.name

# class Mail(Action):
#     subject = models.CharField(max_length=250, null=True, blank=True)
#     attachment = models.FileField(null=True, blank=True, upload_to="attachment")
#     receiver_mail = models.EmailField(null=True, blank=True)
#     sender_mail = models.EmailField(null=True, blank=True)
#
#     class Meta:
#         unique_together = (
#         'name', 'subject', 'description', 'sender_mail', 'receiver_mail', 'schedule_time')
#
#     def __str__(self):
#         return self.name
#
#
# class Reminder(Action):
#     email = models.EmailField(null=True, blank=True)
#
#     class Meta:
#         unique_together = ('name', 'email', 'description', 'schedule_time')
#
#     def __str__(self):
#         return self.email
#
#
# class Message(Action):
#     phone_number = models.CharField(max_length=50, null=True, blank=True)
#     sender = models.CharField(max_length=200, null=True, blank=True)
#
#     class Meta:
#         unique_together = ('name', 'phone_number', 'description', 'sender', 'schedule_time')
#
#     def __str__(self):
#         return self.name
