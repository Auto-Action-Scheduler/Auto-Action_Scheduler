from django.db import models
from django.utils import timezone


# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_deleted=False)


class DeleteManager(models.Manager):
    def get_queryset(self):
        return super(DeleteManager, self).get_queryset().filter(is_deleted=True)


class Action(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    schedule_time = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_executed = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Mail(Action):
    subject = models.CharField(max_length=250)
    attachment = models.FileField(null=True, blank=True, upload_to="attachment")
    receiver_mail = models.EmailField()
    sender_mail = models.EmailField()

    class Meta:
        unique_together = (
        'name', 'subject', 'description', 'sender_mail', 'receiver_mail', 'schedule_time')

    def __str__(self):
        return self.name


class Reminder(Action):
    email = models.EmailField()

    class Meta:
        unique_together = ('name', 'email', 'description', 'schedule_time')

    def __str__(self):
        return self.email


class Message(Action):
    phone_number = models.CharField(max_length=50)
    sender = models.CharField(max_length=200)

    class Meta:
        unique_together = ('name', 'phone_number', 'description', 'sender', 'schedule_time')

    def __str__(self):
        return self.name
