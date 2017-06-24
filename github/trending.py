import sys

import irc.client
import lxml.html
import requests

def get_trending(language):
    url = 'https://github.com/trending/' + language
    response = requests.get(url)
    html = lxml.html.fromstring(response.text)
    lines = []
    for item in html.cssselect('.repo-list li'):
        name = ''.join(item.cssselect('h3')[0].text_content().split())
        repo = 'https://github.com/' + name
        desc = item.cssselect('p')[0].text.strip()
        meta = item.cssselect('span .octicon-star')
        star = None
        if meta:
            star = meta[0].tail.strip()
        if star is None:
            break
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
        for line in get_trending('rust'):
            self.connection.privmsg(self.channel, line)
        self.connection.quit()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--irc', action='store_true')
parser.add_argument('language')
args = parser.parse_args()

if args.irc:
    client = Trending('#rust')
    client.connect('irc.ozinger.org', 6667, 'rustbot')
    client.start()
else:
    for line in get_trending(args.language):
        print line
