import sys

import irc.client
import lxml.html
import requests

def get_trending(language):
    url = 'https://github.com/trending/' + language
    response = requests.get(url)
    html = lxml.html.fromstring(response.text)
    lines = []
    for item in html.cssselect('.repo-list-item'):
        d = dict((child.get('class'), child) for child in item)
        name = ''.join(d['repo-list-name'].text_content().split())
        repo = 'https://github.com/' + name
        desc = None
        if 'repo-list-description' in d:
            desc = d['repo-list-description'].text.strip()
        # U+2022 BULLET
        meta = d['repo-list-meta'].text.split(u'\u2022')
        star = None
        if len(meta) == 3 and 'star' in meta[1]:
            star = meta[1].strip()
        if star is None:
            break
        if desc is None:
            line = '[trending] %s (%s)' % (repo, star)
        else:
            line = '[trending] %s - %s (%s)' % (repo, desc, star)
        lines.append(line)
    return lines

class Trending(irc.client.SimpleIRCClient):
    def __init__(self, channel):
        irc.client.SimpleIRCClient.__init__(self)
        self.channel = channel
    def on_welcome(self, *args):
        self.connection.join(self.channel)
    def on_join(self, *args):
        self.go()
    def on_disconnect(self, *args):
        sys.exit()
    def go(self):
        lines = get_trending('rust')
        for line in lines:
            self.connection.privmsg(self.channel, line)
        self.connection.quit()

client = Trending('#rust')
client.connect('irc.ozinger.org', 6667, 'rustbot')
client.start()
