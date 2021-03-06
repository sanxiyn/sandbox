import email.utils
import urllib.parse

import lxml.html
import requests

def from_address(message):
    addr = message['From']
    mail = email.utils.parseaddr(addr)[1]
    return mail

def from_domain(message):
    mail = from_address(message)
    domain = mail.rpartition('@')[-1]
    domain = domain.lower()
    return domain

def from_name(message):
    addr = message['From']
    name = email.utils.parseaddr(addr)[0]
    return name

def from_subject(message):
    subject = message['Subject']
    return subject

def date_timestamp(message):
    date = message['Date']
    parsed = email.utils.parsedate_tz(date)
    timestamp = email.utils.mktime_tz(parsed)
    return timestamp

def extract_url(message):
    assert message.get_content_type() == 'text/plain'
    url = message.get_payload().strip()
    assert urllib.parse.urlparse(url).scheme == 'http'
    return url

def title_of_url(url):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return 'connection error'
    status = response.status_code
    if status != 200:
        return 'status {}'.format(status)
    content_type = response.headers['Content-Type']
    content_type = content_type.partition(';')[0]
    assert content_type == 'text/html'
    html = lxml.html.fromstring(response.text)
    matches = html.cssselect('title')
    if not matches:
        return 'no title'
    assert len(matches) == 1
    title = matches[0].text
    return title
