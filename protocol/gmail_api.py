import httplib2

from google.cloud import pubsub

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from django.conf import settings

CLIENT_SECRET_FILE = settings.GMAIL_API_SECRET_FILE
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
APPLICATION_NAME = 'Gmail API Python Quickstart'

#pubsub_client = pubsub.Client()

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = Storage(CLIENT_SECRET_FILE)
    credentials = store.get()
    return credentials


def get_service(credentials, service='gmail'):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build(service, 'v1', http=http)
    return service


def watch_notifications(service):
    request = {
      'labelIds': ['INBOX'],
      'topicName': TOPIC_NAME #'projects/correspondence-protocol-system/topics/get_messages'
    }
    return service.users().watch(userId='me', body=request).execute()