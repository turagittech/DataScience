#!/usr/bin/env python
#
# Very basic example of using Python 3 and IMAP to iterate over emails in a
# gmail folder/label.  This code is released into the public domain.
#
# This script is expanded on the sample code from this blog post:
# http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
#
# This is an updated version of the original -- modified to work with Python 3.4.
# Improved to support IMAP across mailboxes
# Get email account  connection data from json config file
#
import sys
import imaplib
import getpass
import email
import email.header
import datetime
import json
import getopt


EMAIL_ACCOUNT = "xxxx@turagit.com"
IMAP_HOST = "imap.google.com"
SSL = "y"
IMAP_PORT =930
EMAIL_PASSWORD = ''
CFG_FILE = 'email_cfg.json'

# Use 'INBOX' to read inbox.  Note that whatever folder is specified,
# after successfully running this script all emails in that folder
# will be marked as read. Archives/2018
EMAIL_FOLDER = "INBOX"


def get_parameters():
    """
    Get Command Line parameter for cfg file location

    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], ["cfg="])
    except getopt.GetoptError as err:
        #print Error Message
        print(err)
        sys.exit(2)
    filename = args

    return



def get_config():
    """
        Retrive credentials from config file
    """
    with open(CFG_FILE, "r") as cfg_file:
        email_cfg = json.load(cfg_file)
        for e in email_cfg['emailconfig']:
            EMAIL_ACCOUNT = e['emailaddress']
            EMAIL_FOLDER =  e['emailfolder']
            IMAP_HOST = e['imaphost']
            IMAP_PORT = e['imapport']
            SSL = e['ssl']
            EMAIL_PASSWORD = e['emailpwd']
            print(EMAIL_ACCOUNT, EMAIL_FOLDER, IMAP_HOST, IMAP_PORT, SSL, EMAIL_PASSWORD )



    return


def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        print('Message %s: %s' % (num, subject))
        print('Raw Date:', msg['Date'])
        # Now convert to local date-time
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple))
            print ("Local Date:", \
                local_date.strftime("%a, %d %b %Y %H:%M:%S"))


M = imaplib.IMAP4_SSL(IMAP_HOST)

try:
    #rv, data = M.login(EMAIL_ACCOUNT, getpass.getpass())
    rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
except imaplib.IMAP4.error:
    print ("LOGIN FAILED!!! ")
    sys.exit(1)

print(rv, data)

rv, mailboxes = M.list()
if rv == 'OK':
    print("Mailboxes:")
    print(mailboxes)

rv, data = M.select(EMAIL_FOLDER)
if rv == 'OK':
    print("Processing mailbox...\n")
    process_mailbox(M)
    M.close()
else:
    print("ERROR: Unable to open mailbox ", rv)

M.logout()