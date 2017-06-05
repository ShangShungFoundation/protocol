import contextio as c

from django.conf import settings

context_io = c.ContextIO(
    consumer_key=settings['CONTEXTIO'].CONSUMER_KEY,
    consumer_secret=settings['CONTEXTIO'].CONSUMER_SECRET,
    api_version=settings['CONTEXTIO'].API_VERSION
)

def get_emails(email):
    # https://github.com/contextio/Python-ContextIO
    accounts = context_io.get_accounts(email=email)
    if accounts:
        account = accounts[0]
        account.get()
        