import collections
import email

from imapclient import IMAPClient

import utils

host = 'imap.gmail.com'

with open('username') as f:
    username = f.read()

with open('password') as f:
    password = f.read()

import sys
args = sys.argv[1:]
if len(args) != 1:
    print 'Usage: domain.py folder'
    sys.exit()
folder, = args

imap = IMAPClient(host, ssl=True)
imap.login(username, password)
imap.select_folder(folder)
msgids = imap.search()
response = imap.fetch(msgids, ['BODY.PEEK[HEADER]'])
messages = []
for msgid in msgids:
    header = response[msgid]['BODY[HEADER]']
    message = email.message_from_string(header)
    messages.append(message)

counter = collections.Counter()
counter.update(utils.from_domain(message) for message in messages)
for domain, count in counter.most_common():
    print domain, count
