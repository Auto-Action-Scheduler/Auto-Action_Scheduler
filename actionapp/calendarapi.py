from __future__ import print_function

import os.path
import google_auth_oauthlib.flow

from decouple import config
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def sync_event(request, name, description, schedule_time):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    state = request.GET.get('state', None)

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            flow.redirect_uri = config('GOOGLE_REDIRECT_URL')
            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
            # creds = flow.run_local_server(port=0)
            # print(vars(request))
            authorization_response = "https://autoactionschedulerapp.herokuapp.com/api/action/create-list"
            print('response', type(authorization_response))
            # print(request.GET.get('state'))
            # print(request.GET.get('_google_authlib_state_'))
            # code = request.GET.get('code')
            # print(code)
            flow.fetch_token(authorization_response=authorization_response)
            creds = flow.credentials
            # print(authorization_url)
        # Save the credentials for the next run
        # with open('token.json', 'a+') as token:
        #     token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': name,  # event's title
            'description': description,  # event's description
            'start': {
                'dateTime': schedule_time,
                'timeZone': 'Africa/Lagos',
            },  # event's start date/time with timezone
            'end': {
                'dateTime': schedule_time,
                'timeZone': 'Africa/Lagos',
            },  # event's end date/time with timezone
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        events = service.events().insert(calendarId='primary', body=event).execute()

        return events

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    sync_event()