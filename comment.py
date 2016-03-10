
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

import os
import re
import pdb


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
    print('Getting the upcoming 2000 events')
    eventsResult = service.events().list(
        calendarId='hppom46juulm7qs75s461b83t4@group.calendar.google.com', timeMin=now, maxResults=2000, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
	
    username, password = "BOT_USERNAME", "BOT_PASSWORD"
    subreddit = "mscalstest"

    r = praw.Reddit("MSCals Comments 0.1")

    print ("Logging in")
    r.login(username,password)
    subreddit=r.get_subreddit(subreddit)
    subreddit_comments = subreddit.get_comments()
    
    import os
	
	#Check for comments list file, create if necessary
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
    # Read the file into a list and remove any empty values  
        with open("comments_replied_to.txt", "r") as f:
            comments_replied_to = f.read()
            comments_replied_to = comments_replied_to.split("\n")
            comments_replied_to = list(filter(None, comments_replied_to))

    #Check for comments containing ?next in body
    for comment in subreddit_comments:
        mainComm = comment.body.lower()
        if comment.id not in comments_replied_to:
            if "?next" in mainComm:
                sl=list()
                if not events:
                    print('No upcoming events found.')
                for event in events:
                    #Check for race request or event request. Format data returned
                    if "?nextrace" in mainComm: 			
                        if mainComm.split("race",1)[1].strip() in event['summary'].lower():
                            if "race" in event['summary'].lower():
                                start = event['start'].get('dateTime', event['start'].get('date'))
                                actEv = start[8:10]+'/'+start[5:7]+'/'+start[0:4]+' '+start[11:16]+' - '+event['summary']
                                sl.append(actEv)
                    elif "?nextevent" in mainComm:
                        if mainComm.split("event",1)[1].strip() in event['summary'].lower():
                            start = event['start'].get('dateTime', event['start'].get('date'))
                            actEv = start[8:10]+'/'+start[5:7]+'/'+start[0:4]+' '+start[11:16]+' - '+event['summary']
                            sl.append(actEv)
                
                #Account for no events, or write only next event				
                if len(sl) == 0:
                    comment.reply("No event in the near future")
                else:
                    comment.reply(sl[0])
            comments_replied_to.append(comment.id)  
			
    #write comment reply                   
    with open("comments_replied_to.txt", "w") as f:
        for comment_id in comments_replied_to:
            f.write(comment_id + "\n")                   
			
if __name__ == '__main__':
    main()
    
	
