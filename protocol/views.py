import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail

from gmail_api import get_credentials, get_service, watch_notifications

from models import Category, Communication

#credentials = get_credentials()
#gmail_service = get_service(credentials, 'gmail')

def watch(request):
    """orders watching gmail. 
    has to be invoked at least once a week
    """
    notifications_status = watch_notifications()
    if notifications_status:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)


def notify_message(request):
    #content = json.loads(request.POST)
    return HttpResponse(status=200)


PROTOCOL_CATEGORY_NOT_FOUND = u"Protocol category has not been found."
PROTOCOL_CATEGORY_NOT_FOUND_MSG = u"""Protocol category has not been found in the email subject. 
Please prefix protocol category to the email subject. like: '#ORG-SSF/2/' """
PROTOCOL_WRONG_CATEGORY = u"Protocol category #%s has not been found."
PROTOCOL_WRONG_CATEGORY_MSG = u"""Category #%s does not correspond to any registered protocol category. 
Please make sure you got it spelled correctly"""

def return_email(sbj, msg):
    send_mail(sbj, msg, ADMIN_EMAIL, ['m.kocylowski@shangshunginstitute.org'], fail_silently=False)

#def protocol_request(sender, request_msg):


def list_categories(request):
    categories = Category.objects.all()
    cats = [[c.path, c.name] for c in categories]
    return JsonRespone(cats)


def show_categories(request):
    categories = Category.objects.all()
    cats = [[c.path, c.name]  for c in categories]
    return render("protocol/categories.html", cats)


def process_request_msg(sender, request_msg):
    sbj = msg = u""
    sucess = False
    category_reg = re.compile(r'^\d*#(?P<protocol_id>[0-9a-zA-Z\-\/]+) .*')
    category_id = protocol_reg.match(category_reg)

    if not category_id:
        sbj = PROTOCOL_CATEGORY_NOT_FOUND
        msg = PROTOCOL_CATEGORY_NOT_FOUND_MSG
        return return_email(sbj, msg)

    category = Category.objects.get(path=category_id)
    if not category:
        sbj = PROTOCOL_WRONG_CATEGORY % category_id
        msg = PROTOCOL_WRONG_CATEGORY_MSG % category_id
        return return_email(sbj, msg)

    comm = Communication.objects.create(
        category=category,
        frm=frm,
        to=to,
        subject=subject,
        is_incoming=is_incoming
    )

    return_email(sbj, msg)

def google_auth(request):
    """orders watching gmail. 
    has to be invoked at least once a week
    """
    return HttpResponse("google-site-verification: google6fbfc2fc692f39fc.html", status=200)






