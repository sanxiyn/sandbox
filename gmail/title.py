import collections
import email
import multiprocessing

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
    print 'Usage: title.py folder'
    sys.exit()
folder, = args

imap = IMAPClient(host, ssl=True)
imap.login(username, password)
imap.select_folder(folder)
msgids = imap.search()
response = imap.fetch(msgids, ['BODY.PEEK[]'])
messages = []
for msgid in msgids:
    header = response[msgid]['BODY[]']
    message = email.message_from_string(header)
    messages.append(message)

counter = collections.Counter()
pool = multiprocessing.Pool()
urls = [utils.extract_url(message) for message in messages]
counter.update(pool.imap(utils.title_of_url, urls))
for title, count in counter.most_common():
    print title, count
