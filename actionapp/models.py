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
    schedule_time = models.DateTimeField(default=timezone.now())
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_executed = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    def __str__(self):
        return self.name


class Mail(Action):
    subject = models.CharField(max_length=250)
    attachment = models.FileField(null=True, blank=True, upload_to="attachment")
    receiver_mail = models.EmailField()
    sender_mail = models.EmailField()

    def __str__(self):
        return self.name


class Reminder(Action):
    email = models.EmailField()

    def __str__(self):
        return self.email


class Message(Action):
    phone_number = models.CharField(max_length=50)
    sender = models.CharField(max_length=200)

    def __str__(self):
        return self.name
