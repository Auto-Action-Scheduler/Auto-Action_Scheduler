from django.core.mail import send_mail
from django.utils.baseconv import base64
from django.utils import timezone

from decouple import config
from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

from AutoActionScheduler.celery import app
from actionapp.models import Mail


@app.task()
def every_hour_task():
    mails = Mail.active_objects.exclude(is_executed=True)
    now = timezone.now()

    for mail in mails:
        if mail.schedule_time.date() == now.date() and mail.schedule_time.hour == now.hour:
            send_email.apply_async((mail.pk,),
                                   eta=timezone.datetime(year=mail.schedule_time.year, month=mail.schedule_time.month,
                                                         day=mail.schedule_time.day,
                                                         hour=mail.schedule_time.hour,
                                                         minute=mail.schedule_time.minute,
                                                         second=mail.schedule_time.second))



@app.task()
def send_email(pk):
    mail = Mail.active_objects.exclude(is_executed=True).filter(id=pk).first()

    if mail:
        send_mail(subject=mail.subject, message=mail.description, from_email=mail.sender_mail,
                  recipient_list=[mail.receiver_mail])
        mail.is_executed = True
        mail.save()

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
