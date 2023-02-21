from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def sync_event(name, description, schedule_time):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            flow.redirect_uri = 'http://localhost/api/action/'
            creds = flow.run_local_server(port=0)
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