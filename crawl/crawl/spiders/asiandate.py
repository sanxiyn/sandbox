import urlparse

import scrapy

def get(element, attr):
    return element.xpath('./@{}'.format(attr)).extract()[0]

def resolve(response, image):
    return urlparse.urljoin(response.url, get(image, 'href'))

def get_value(response, key):
    url = response.url
    if 'redirect_urls' in response.meta:
        url = response.meta['redirect_urls'][0]
    query = urlparse.urlsplit(url).query
    return urlparse.parse_qs(query)[key][0]

class AsianDateSpider(scrapy.Spider):
    name = 'asiandate'

    def __init__(self, start=None, end=None):
        if start is None:
            raise Exception('start is required')
        if end is None:
            raise Exception('end is required')
        self.start = int(start)
        self.end = int(end)

    def start_requests(self):
        for i in range(self.start, self.end):
            url = 'http://www.asiandate.com/pages/lady/profile/profilepreview.aspx?LadyID={}'.format(i)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        if 'profile-is-unavailable' in response.url:
            return
        id = get_value(response, 'LadyID')
        thumbnail = response.css('.lady-star-name div.lady-thumbnail-container img')[0]
        profiles = response.css('div.photo-wrapper img')
        yield {
            'id': '{}-{}-{}'.format(self.name, id, 'thumbnail'),
            'url': resolve(response, thumbnail)
        }
        yield {
            'id': '{}-{}-{}'.format(self.name, id, 'profile1'),
            'url': resolve(response, profiles[0])
        }
        yield {
            'id': '{}-{}-{}'.format(self.name, id, 'profile2'),
            'url': resolve(response, profiles[1])
        }
