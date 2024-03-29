import argparse
import urllib.parse

import lxml.html
import requests

def search(topic):
    if ' ' in topic:
        topic = f'"{topic}"'
    topic = urllib.parse.quote(topic)
    url = 'https://lobste.rs/search?what=stories&order=newest&q=' + topic
    response = requests.get(url)
    html = lxml.html.fromstring(response.text)
    count = html.cssselect('.heading')[0].text_content().strip()
    count = ' '.join(count.split(' ')[:2])
    print(count)
    for item in html.cssselect('.link a'):
        text = item.text_content()
        print(f' * {text}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic', nargs='*')
    args = parser.parse_args()
    topic = ' '.join(args.topic)
    search(topic)
