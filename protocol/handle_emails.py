import json
import email
import imaplib
import re
import os
from io import BytesIO

from email.mime.message import MIMEMessage

from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Category, Communication, Document

from django.conf import settings

PROTOCOL_FROM = 'SSF Protocol System <protocol@shangshunginstitute.org>'
PROTOCOL_CATEGORY_NOT_FOUND = u"Protocol category has not been found."
PROTOCOL_CATEGORY_NOT_FOUND_MSG = u"""Protocol category has not been found in the email subject. 
Please prefix protocol category to the email subject. like: '/ORG/2/2/' """
PROTOCOL_WRONG_CATEGORY = u"Protocol category '%s' not found."
PROTOCOL_WRONG_CATEGORY_MSG = u"""Category '%s' does not correspond to any registered protocol category. 
Please make sure you got it spelled correctly"""
PROTOCOL_CAT_NOT_ALLOWED = "Protocol category '%s' does not allows posting"
PROTOCOL_CAT_NOT_ALLOWED_MSG = "Protocol category '%s' does not allows posting"
PROTOCOL_REF_NOT_FOUND = u"Protocol '%s' not found."
PROTOCOL_REF_NOT_FOUND_MSG = u"""Protocol reference %s has not been found in the email subject. 
Please check its spelling"""
PROTOCOL_ALLOWED_DOMAINS = ["shangshunginstitute.org", "shangshungfoundation.org"]
PROTOCOL_SENDER_NOT_ALLOWED = "'%s' sender not allowed"
PROTOCOL_DOMAIN_NOT_ALLOWED_MSG = "'%s' sender domain not allowed"

PROTOCOL_REF_FOUND = "Message '%s' has been added to existing protocol"
PROTOCOL_REF_FOUND_MSG = """Your message 
'%s' 
has been added to the existing corespondence protocol ref: '%s'
at %s"""
PROTOCOL_REF_CREATED = "Email '%s' has been added to the protocol"
PROTOCOL_REF_CREATED_MSG = """Email '%s' 
has been added to the protocol with ref: '%s'
at %s"""


def notify(msg, to, original):
    new = EmailMultiAlternatives("Re: "+ original["Subject"].replace("\r\n", " "),
         msg, 
         PROTOCOL_FROM, # from
         to, # to
         headers = {'Reply-To': original["From"],
                    "In-Reply-To": original["Message-ID"],
                    "References": original["Message-ID"]})
    # new.attach_alternative("<html>reply body text</html>", "text/html")
    # new.attach( MIMEMessage(original) ) # attach original message
    try:
        new.send()
    except smtplib.SMTPDataError:
        import ipdb; ipdb.set_trace()


def is_allowed_sender(frm):
    from_pattern = re.compile(r'^.+@([\w\.]+).*$')
    domain = from_pattern.findall(frm)[0]
    return domain in PROTOCOL_ALLOWED_DOMAINS

def get_unseen_emails():
    # https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
    output = []
    mailbox = imaplib.IMAP4_SSL('imap.gmail.com','993')
    mailbox.login(settings.PROTOCOL_EMAIL, settings.PROTOCOL_EMAIL_PASS)
    mailbox.select()
    result, data = mailbox.search(None, 'UnSeen')  #'UnSeen') # "ALL"
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string
    
    for e in id_list:
        result, data = mailbox.fetch(e, "(RFC822)") # fetch the email body (RFC822) for the given ID
        email_message = email.message_from_bytes(data[0][1])
        # raw_data = str(data[0][1]).replace("\\r\\n", "\r\n")
        # email_message = email.message_from_string(raw_data)
        success, communication = process_request_msg(mailbox, email_message)
        if success:
            documents = process_email(communication, email_message)
        output.append([success, "%s" % communication.protocol if success else communication])
    mailbox.close()
    mailbox.logout()
    return output


def list_categories(request):
    categories = Category.objects.all()
    cats = [[c.path, c.name] for c in categories]
    return JsonRespone(cats)


def show_categories(request):
    categories = Category.objects.all()
    cats = [[c.path, c.name]  for c in categories]
    return render("protocol/categories.html", cats)


def strip_original(original):
    # https://stackoverflow.com/questions/2182196/how-do-i-reply-to-an-email-using-the-python-imaplib-and-include-the-original-mes
    for part in original.walk():
        if (part.get('Content-Disposition') 
            and part.get('Content-Disposition').startswith("attachment")):

            part.set_type("text/plain")
            part.set_payload("Attachment removed: %s (%s, %d bytes)"
                    %(part.get_filename(), 
                    part.get_content_type(), 
                    len(part.get_payload(decode=True))))
            del part["Content-Disposition"]
            del part["Content-Transfer-Encoding"]
    return original


def process_request_msg(mailbox, request_msg):
    sbj = msg = u""
    success = False
    communication = None
    category = None
    protocol_path = ""
    subject_text = ""
    subject = request_msg['Subject']
    frm = request_msg['From']
    all_recipients = email.utils.getaddresses(request_msg.get_all('to', []))
    recipients_list =[]
    to = []
    for n, e in all_recipients:
        email_to = "%s <%s>" % (n, e)
        if e == settings.PROTOCOL_EMAIL:
            continue
        if email_to == frm:
            continue
        recipients_list.append((n, e))
        to.append(email_to)
    
    # to = request_msg['To'].replace(", \r\n\t%s" % PROTOCOL_FROM, "").replace("\r\n\t", "")
    notify_emails = [frm]
    
    #stripped_original = strip_original(request_msg)

    if not is_allowed_sender(frm):
        return False, PROTOCOL_SENDER_NOT_ALLOWED % frm

    # we check for protocol category reference
    try:
        category_ref, subject_text = re.search(
            r"^ *(?P<protocol_id>[0-9a-zA-Z\/]+\/) (?P<subject>.*)$", subject).groups()
    except:
        sbj = PROTOCOL_CATEGORY_NOT_FOUND
        msg = PROTOCOL_CATEGORY_NOT_FOUND_MSG
    else:
        # we check for protocol if category exist
        try:
            category = Category.objects.get(reference=category_ref)
        except Category.DoesNotExist:
            sbj = PROTOCOL_WRONG_CATEGORY % category_ref
            msg = PROTOCOL_WRONG_CATEGORY_MSG % category_ref
        else:
            if category.allows_storage:
                metadata=dict(request_msg.items())
                #del(metadata["b'Delivered-To"])  #HACK 
                communication = Communication(
                    category=category,
                    frm=frm,
                    to=", ".join(to),
                    subject=subject_text,
                    is_incoming=True,
                    is_digital=True,
                    metadata=json.dumps(metadata)
                )
                communication.save()
                success = True
                sbj = PROTOCOL_REF_CREATED % subject_text
                msg = PROTOCOL_REF_CREATED_MSG % (
                    subject_text, communication.protocol, communication.protocol)
                notify_emails = notify_emails + to
            else:
                sbj = PROTOCOL_CAT_NOT_ALLOWED % category_ref
                msg = PROTOCOL_CAT_NOT_ALLOWED_MSG % category_ref
            

    if not communication:
        # we check for particular protocol reference
        try:
            protocol_ref, subject_text = re.search(
                r"^ *(?P<protocol_id>[0-9a-zA-Z\/]+)/(\d\d\d\d-\d+) (?P<subject>.*)$", subject).groups()
        except UnboundLocalError:
            sbj = PROTOCOL_WRONG_CATEGORY % ""
            msg = PROTOCOL_WRONG_CATEGORY_MSG % ""
        except AttributeError:
            sbj = PROTOCOL_WRONG_CATEGORY % ""
            msg = PROTOCOL_WRONG_CATEGORY_MSG % ""
        else:
            # we check if particular protocol reference is alredy present
            try:
                communication = Communication.objects.get(protocol=protocol_ref)
            except:
                sbj = PROTOCOL_REF_NOT_FOUND % protocol_ref
                msg = PROTOCOL_REF_NOT_FOUND_MSG % protocol_ref
            else:
                success = True
                sbj = PROTOCOL_REF_FOUND % subject_text
                msg = PROTOCOL_REF_FOUND_MSG % (
                    subject_text, communication.protocol, communication.protocol)
                notify_emails = notify_emails + to
    
    notify(msg, notify_emails, request_msg)
    return success, communication if success else sbj


def process_email(communication, m):
    docs = []
    for part in m.walk():
        ctype = part.get_content_type()
        cdispo = part.get_content_disposition()   #str(part.get('Content-Disposition'))
        filename=part.get_filename()
        if ctype in ['text/plain', 'text/html'] and not filename:
            metadata = dict(part.items())
            doc = Document(
                communication=communication,
                message_id=part["Message-ID"],
                body=part.get_payload(),
                metadata=json.dumps(metadata)
            )
            doc.save()
            docs.append(doc)
        
        if filename:
            # storage_dir = os.path.join(communication.storage_dir, filename)
            # storage_path = os.path.join(settings.MEDIA_ROOT, storage_dir)
            # os.makedirs(os.path.join(settings.MEDIA_ROOT, communication.storage_dir))
            # if not os.path.isfile(storage_path):
            doc = Document(
                communication=communication,
                message_id=part['X-Attachment-Id'],
            )
            #import ipdb; ipdb.set_trace()
            attachment = BytesIO()
            attachment.write(part.get_payload(decode=True))
            doc.attachment.save(filename, File(attachment), save=True)
                # with open(storage_path, 'w+') as fp:
                #     fp.write(part.get_payload(decode=True))
                # open(storage_path, 'wb').write(part.get_payload(decode=True))
                # # doc.attachment.save(filename, part.get_payload(decode=True))
                # doc.attachment = storage_dir
            doc.save()
            docs.append(doc)
    return docs