from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
import praw
import requests
from html.parser import HTMLParser
import html

import datetime
import time

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

# Google Authentication stuff
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 100 events')
    eventsResult = service.events().list(
        calendarId='hppom46juulm7qs75s461b83t4@group.calendar.google.com', timeMin=now, maxResults=100, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
	
    username, password = "BOT_USERNAME", "BOT_PASSWORD"
    subreddit = "mscalstest"

    r = praw.Reddit("MSCals Sidebar 0.1")

    print ("Logging in")
    r.login(username,password)
    subreddit=r.get_subreddit(subreddit)

    sl=list()
	
    if not events:
        print('No upcoming events found.')
    for event in events:
	    #Grab title and location from event, then filter by events that much current week number
        start = event['start'].get('dateTime', event['start'].get('date'))
        place = event['location'].split(', ',1)[1]
        shortEV = event['summary'].rsplit(place,1)[0] + '|' + place
        eventsMonth = datetime.date(int(start[0:4]), int(start[5:7]), int(start[8:10])).isocalendar()[1]
        currMonth = datetime.date.today().isocalendar()[1]
        if (eventsMonth == currMonth):
            sl.append(shortEV)

    #Very possibly redundant, from old code	
    try:
        config = html.unescape(r.get_wiki_page(subreddit,"sidebar_bot_config").content_md)
    except requests.exceptions.HTTPError:
        print ("Couldn't access format wiki page, reddit may be down.")
        raise

    #Remove duplicate events and reorganise
    sl = (list(set(sl)))
    sl.sort()
	
    #Cycle through series, pull any events matching series name. Keep first and last event date, create formatted date
    for i in range (0,len(sl)):
        sldate = list()
        for event in events:        
            if sl[i].split('|',1)[0] in event['summary']:   
                sldate.append(event['start'].get('dateTime', event['start'].get('date'))) 
        intDate = sldate[0]
        finDate = sldate[-1]
        if (intDate[5:10] == finDate[5:10]): 
            compDate = intDate[8:10]+'/'+intDate[5:7]
        else:
            compDate = intDate[8:10]+'-'+finDate[8:10]+'/'+intDate[5:7]
        print(sl[i].split('|',1)[0], compDate)
        sl[i]= sl[i]+'|'+compDate
    sidebar_string = '\n'.join(sl)

    #Update sidebar table
    print ("Updating sidebar")
    sidebar = r.get_settings(subreddit)
    submit_text = html.unescape(sidebar["submit_text"])
    desc = html.unescape(sidebar['description'])
    startmarker, endmarker = desc.index("[](#StartMarker2)"), desc.index("[](#MarkerEnd2)") + len("[](#MarkerEnd2)")
    updated_desc = desc.replace(desc[startmarker:endmarker], "[](#StartMarker2)" + sidebar_string + "[](#MarkerEnd2)")
    
    if updated_desc != desc:
        subreddit.update_settings(description=updated_desc.encode('utf8'), submit_text=submit_text)
	
		
if __name__ == '__main__':
    main()
    
	
