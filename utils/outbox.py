import requests
from decouple import config

from actionapp.models import Action


def send_sms(pk):
    sms = Action.active_objects.filter(action_type='SMS').exclude(is_executed=True, is_scheduled=False).filter(id=pk).first()
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
        "to": sms.phone_number
    }

    response = requests.post(url=url, headers=headers, data=data)
    sms.is_executed = True
    sms.save()
