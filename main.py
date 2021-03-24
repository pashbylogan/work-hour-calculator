#!/usr/bin/env python3

import datetime
import yaml
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def getCreds():
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# getPayRange - Calculates the pay range of interest given today's date (options are represented in config.yaml)
# Input: N/A
# Output: datetime objects for beginning and end of range
def getPayRange():
    with open('config.yaml') as f:
        data = yaml.load(f,Loader=yaml.FullLoader)
        today = datetime.datetime.now()
        for list in data['payPeriods']:
            startDate = datetime.datetime(int(list[0].split("-")[0]), int(list[0].split("-")[1]), int(list[0].split("-")[2]), 00, 00, 00, 0).isoformat() + data['timezone']
            endDate = datetime.datetime(int(list[1].split("-")[0]), int(list[1].split("-")[1]), int(list[1].split("-")[2]), 23, 59, 59, 0).isoformat() + data['timezone']
            start = datetime.datetime.strptime(list[0],"%Y-%m-%d")
            end = datetime.datetime.strptime(list[1], "%Y-%m-%d")
            if start <= today <= end:
                return startDate,endDate
        return None,None

# getManualPayRange - Same as getPayRange, except returns datetime objects given user input
# Input: Two user-defined dates
# Output: datetime objects for beginning and end of range
def getManualPayRange(start,end):
    with open('config.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        startDate = datetime.datetime(int(start.split("-")[0]), int(start.split("-")[1]), int(start.split("-")[2]), 00, 00, 00, 0).isoformat() + data['timezone']
        endDate = datetime.datetime(int(end.split("-")[0]), int(end.split("-")[1]), int(end.split("-")[2]), 23, 59, 59, 0).isoformat() + data['timezone']
    return startDate, endDate

def main():
    creds = getCreds()
    service = build('calendar', 'v3', credentials=creds)

    # Takes input from user and tries to generate datetime objects
    startDate = None
    while (startDate == None):
        if (input('Do you want to input dates? (y/n) ').lower() == 'y'):
            startDate,endDate = getManualPayRange(input('Enter first date (Y-m-d): '),input('Enter second date (Y-m-d): '))
        else:
            startDate,endDate = getPayRange()

        if startDate == None:
            print("Those dates don't work. Try Again.")

    # Query the Google Calendar API
    events_result = service.events().list(calendarId='primary', timeMin=startDate,
                                          singleEvents=True,
                                          orderBy='startTime', timeMax=endDate).execute()
    events = events_result.get('items', [])

    # Don't do anything if there aren't any work events in the given range
    if not events:
        print('No upcoming events found.')
    week1Sum, week2Sum=0,0
    for event in events:
        if 'tcc' in event['summary'].lower():
            # Print the name, date, and time bounds of event
            print('{:<8}\n\t{:<8}\n\t{:<8} {:<8}'.format(event['summary'],
                    event['start'].get('dateTime').split("T")[0][5:],
                    event['start'].get('dateTime').split("T")[1][:5],
                    event['end'].get('dateTime').split("T")[1][:5]))

            # timedelta objects will help add total hours
            t1 = datetime.timedelta(hours=int(event['start'].get('dateTime').split("T")[1][:2]),
                                                minutes=int(event['start'].get('dateTime').split("T")[1][3:5]),
                                                seconds=int(event['start'].get('dateTime').split("T")[1][6:8]))
            t2 = datetime.timedelta(hours=int(event['end'].get('dateTime').split("T")[1][:2]),
                                                minutes=int(event['end'].get('dateTime').split("T")[1][3:5]),
                                                seconds=int(event['end'].get('dateTime').split("T")[1][6:8]))

            # Want to keep track of hours per week. 19 hour cap for WWU students.
            if (datetime.datetime.fromisoformat(event['start'].get('dateTime'))
                < datetime.timedelta(days=7)+datetime.datetime.fromisoformat(startDate)):
                week1Sum+=((t2-t1)/datetime.timedelta(minutes=1))
            else:
                week2Sum+=((t2-t1)/datetime.timedelta(minutes=1))

    print('\nWeek 1 hours: ',week1Sum/60)
    print('Week 2 hours: ',week2Sum/60)
    hourSum = week1Sum + week2Sum
    print('Your total hours worked so far is: ',hourSum/60)
    print('Gross revenue = ',hourSum/60*17)



if __name__ == '__main__':
    main()
