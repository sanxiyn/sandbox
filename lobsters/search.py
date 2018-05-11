import lxml.html
import requests

def search(topic):
    url = 'https://lobste.rs/search?what=stories&order=newest&q=' + topic
    response = requests.get(url)
    html = lxml.html.fromstring(response.text)
    for item in html.cssselect('.link a'):
        text = item.text_content()
        print(text)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('topic')
args = parser.parse_args()

search(args.topic)
