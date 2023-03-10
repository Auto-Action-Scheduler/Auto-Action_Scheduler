import json

import africastalking
import requests
from django.core.mail import send_mail
from django.utils.baseconv import base64
from django.utils import timezone

from decouple import config
from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

from AutoActionScheduler.celery import app
from actionapp.calendarapi import sync_event
from actionapp.models import Action


@app.task()
def every_hour_task():
    mails = Action.active_objects.filter(action_type="Mail").exclude(is_executed=True)
    messages = Action.active_objects.exclude(is_executed=True)
    now = timezone.localtime()

    for mail in mails:
        if mail.schedule_time.date() == now.date() and mail.schedule_time.hour == now.hour:
            send_email.apply_async((mail.pk,),
                                   eta=timezone.datetime(year=mail.schedule_time.year, month=mail.schedule_time.month,
                                                         day=mail.schedule_time.day,
                                                         hour=mail.schedule_time.hour,
                                                         minute=mail.schedule_time.minute,
                                                         second=mail.schedule_time.second))
    for message in messages:
        if message.schedule_time.date() == now.date() and message.schedule_time.hour == now.hour:
            send_sms.apply_async((message.pk,), eta=timezone.datetime(year=message.schedule_time.year,
                                                                      month=message.schedule_time.month,
                                                                      day=message.schedule_time.day,
                                                                      hour=message.schedule_time.hour,
                                                                      minute=message.schedule_time.minute,
                                                                      second=message.schedule_time.second))


@app.task()
def send_email(pk):
    mail = Action.active_objects.filter(action_type="Mail").exclude(is_executed=True).filter(
        id=pk).first()

    if mail:
        send_mail(subject=mail.subject, message=mail.description, from_email=mail.email,
                  recipient_list=mail.receiver_mail)
        mail.is_executed = True
        mail.save()


@app.task()
def send_sms(pk):
    sms = Action.active_objects.filter(action_type='SMS').exclude(is_executed=True).filter(
        id=pk).first()
    username = config('SMS_USERNAME')
    api_key = config('SMS_API_KEY')
    url = "https://api.africastalking.com/version1/messaging"
    headers = {
        "apiKey": api_key,
        "Content_Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "username": username,
        "message": sms.description,
        "to": ",".join(sms.phone_number)
    }

    response = requests.post(url=url, headers=headers, data=data)
    sms.is_executed = True
    sms.save()


@app.task()
def sync_reminder(name, description, schedule_time):
    sync_event()


@app.task()
def run_send_mail(from_mail, subject, message, recipient_list):
    send_mail(from_email=from_mail, subject=subject, message=message,
              recipient_list=[recipient_list])

    # message = Mail(
    #     from_email=from_email,
    #     to_emails=to_emails,
    #     subject=subject,
    #     html_content=html_content
    # )
    # with open('attachment.pdf', 'rb') as f:
    #     data = f.read()
    #
    # encoded_file = base64.b64encode(data).decode()
    #
    # attachedFile = Attachment(
    #     FileContent(encoded_file),
    #     FileName('attachment.pdf'),
    #     FileType('application/pdf'),
    #     Disposition('attachment')
    # )
    # message.attachment = attachedFile
    # try:
    #     sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print('Got here')
    #
    #
    # except Exception as e:
    #     print(str(e))


# def send_sms(pk):
#     sms = Message.active_objects.exclude(is_executed=True).filter(id=pk).first()
#     username = config('SMS_USERNAME')
#     api_key = config('SMS_API_KEY')
#     africastalking.initialize(username=username, api_key=api_key)
#
#     sms_message = africastalking.SMS
#
#     if sms:
#         message = sms.description
#         recipient_list = ["+2347063704879"]
#         sender = "6370"
#         try:
#             response = sms_message.send(message, recipient_list, sender)
#             print(response)
#             # sms.is_executed = True
#             # sms.save()
#         except Exception as e:
#             print(e)


# Download the helper library from https://www.twilio.com/docs/python/install
import os
# from twilio.rest import Client
#
# # Set environment variables for your credentials
# # Read more at http://twil.io/secure
# account_sid = "AC0f41d8b59f7b6f1f728919ccdc9bc31e"
# auth_token = "7e6a6445c5030e1f98a9e8c463a623c8"
# client = Client(account_sid, auth_token)
#
# message = client.messages.create(
#   body="Hello from Twilio",
#   from_="+13093544136",
#   to="+2347038521090"
# )
#
# print(message.sid)
