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
import argparse


EMAIL_ACCOUNT = "xxxx@turagit.com"
IMAP_HOST = "imap.google.com"
SSL = "y"
IMAP_PORT =930
EMAIL_PASSWORD = ''


# Use 'INBOX' to read inbox.  Note that whatever folder is specified,
# after successfully running this script all emails in that folder
# will be marked as read. Archives/2018
EMAIL_FOLDER = "INBOX"


def get_parameters():
    """
    Get Command Line parameter for cfg file location

    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--cfg', help='Path to email_cfg.json file for imap settings')
    cfg_file = parser.parse_args()

    return cfg_file.cfg



def get_config(in_cfg_file):
    """
        Retrieve credentials from config file
    """

    with open(in_cfg_file, "r") as cfg_file:
        email_cfg = json.load(cfg_file)

    return email_cfg


def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, 'SUBJECT', '"NETGEAR R8000 Log"')
    if rv != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_bytes(data[0][1])
        email_date = msg['Date']
        # 06 Jan 2018 06:23:00
        dt = datetime.datetime.strptime(email_date, "%d %b %Y %H:%M:%S")
        outfile = 'router_log.' + datetime.datetime.strftime(dt, "%Y%m%d%H%M%S") + '.log'
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        with open(outfile,'w') as f:
            for part in msg.walk():
                if part.get_content_type() =='text/plain':
                    f.write(part.get_payload())

    return


# Main Code here
# Get the command line parameters
CFG_FILE = get_parameters()
# Read config file
email_cfg = get_config(CFG_FILE)

# Convert Dictionary from JSON data to List of values required
cfg_items = list(email_cfg['emailconfig'].values())

EMAIL_ACCOUNT= cfg_items[0]
IMAP_HOST = cfg_items[1]
SSL = cfg_items[2]
EMAIL_FOLDER = cfg_items[3]
EMAIL_PASSWORD = cfg_items[4]
IMAP_PORT = cfg_items[5]


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