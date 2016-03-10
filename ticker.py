
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
    print('Getting the upcoming 50 events')
    eventsResult = service.events().list(
        calendarId='hppom46juulm7qs75s461b83t4@group.calendar.google.com', timeMin=now, maxResults=50, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
	
    username, password = "BOT_USERNAME", "BOT_PASSWORD"
    subreddit = "mscalstest"

    r = praw.Reddit("MSCals Ticker 0.1")

    print ("Logging in")
    r.login(username,password)
    subreddit=r.get_subreddit(subreddit)

    #create string, add Title thing
    sl=list()
    sl.append("Today (GMT):")
    import time
	
    if not events:
        print('No upcoming events found.')
    for event in events:
        #Pull required info from event, then filter on events that match todays date
        start = event['start'].get('dateTime', event['start'].get('date'))
        fullEv = start[11:16] + ' - ' + event['summary']    
        if (time.strftime("%Y-%m-%d") == start[0:10]): 
            sl.append(fullEv)
        print(sl)

    #Account for no events existing on a given day
    if (len(sl) == 1):
	    sl.append("No events")
	
    #Very possibly redundant, from old code	
    try:
        config = html.unescape(r.get_wiki_page(subreddit,"sidebar_bot_config").content_md)
    except requests.exceptions.HTTPError:
        print ("Couldn't access format wiki page, reddit may be down.")
        raise

    sidebar_string = ' | '.join(sl)

    #Updating sidebar section
    print ("Updating sidebar")
    sidebar = r.get_settings(subreddit)
    submit_text = html.unescape(sidebar["submit_text"])
    desc = html.unescape(sidebar['description'])
    startmarker, endmarker = desc.index("[](#StartMarker)"), desc.index("[](#MarkerEnd)") + len("[](#MarkerEnd)")
    updated_desc = desc.replace(desc[startmarker:endmarker], "[](#StartMarker)" + sidebar_string + "[](#MarkerEnd)")
    
    if updated_desc != desc:
        subreddit.update_settings(description=updated_desc.encode('utf8'), submit_text=submit_text)
	
		
if __name__ == '__main__':
    main()
    
	
