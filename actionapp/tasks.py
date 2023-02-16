from decouple import config
from django.utils.baseconv import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
from django.core.mail import send_mail

from AutoActionScheduler.celery import app


@app.task(bind=True, ignore_result=True)
def send_email(from_email=None, to_emails=None, subject='', html_content=''):
    send_mail(subject='Mail Subject', message='mail body', from_email='oyedeleyusuff@gmail.com',
              recipient_list=['yoyedele@afexnigeria.com', ])
    print('Got here')
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


