import collections
import email
import sys
import time

import imapclient
from backports import ssl

import utils

host = 'imap.gmail.com'

with open('username') as f:
    username = f.read()

with open('password') as f:
    password = f.read()

import argparse
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-a', '--address', action='store_true')
group.add_argument('-d', '--domain', action='store_true')
group.add_argument('-n', '--name', action='store_true')
group.add_argument('-s', '--subject', action='store_true')
parser.add_argument('folder')
args = parser.parse_args()

if args.address:
    make_key = utils.from_address
if args.domain:
    make_key = utils.from_domain
if args.name:
    make_key = utils.from_name
if args.subject:
    make_key = utils.from_subject

context = imapclient.create_default_context()
context.verify_mode = ssl.CERT_NONE
imap = imapclient.IMAPClient(host, ssl=True, ssl_context=context)
imap.login(username, password)
imap.select_folder(args.folder)
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
    key = make_key(message)
    timestamp = utils.date_timestamp(message)
    counter[key] = counter[key] + 1
    latest[key] = max(latest[key], timestamp)

for key, count in counter.most_common():
    date = time.strftime('%Y-%m-%d', time.localtime(latest[key]))
    print(key, count, date)
