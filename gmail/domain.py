import collections
import email
import time

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
latest = collections.defaultdict(int)
for message in messages:
    domain = utils.from_domain(message)
    timestamp = utils.date_timestamp(message)
    counter[domain] = counter[domain] + 1
    latest[domain] = max(latest[domain], timestamp)

for domain, count in counter.most_common():
    date = time.strftime('%Y-%m-%d', time.localtime(latest[domain]))
    print domain, count, date
