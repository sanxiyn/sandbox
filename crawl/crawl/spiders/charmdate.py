import urlparse

import scrapy

sorry = 'Sorry, the profile of this lady has already been removed from our website!'

def get(element, attr):
    return element.xpath('./@{}'.format(attr)).extract()[0]

def resolve(response, image):
    return urlparse.urljoin(response.url, get(image, 'src'))

def get_value(response, key):
    query = urlparse.urlsplit(response.url).query
    return urlparse.parse_qs(query)[key][0]

class CharmDateSpider(scrapy.Spider):
    name = 'charmdate'

    def __init__(self, start=None, end=None):
        if start is None:
            raise Exception('start is required')
        if end is None:
            raise Exception('end is required')
        self.start = int(start)
        self.end = int(end)

    def start_requests(self):
        for i in range(self.start, self.end):
            url = 'http://www.charmdate.com/photogallery/woman.php?womanid=C{}'.format(i)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        if sorry in response.body:
            return
        id = get_value(response, 'womanid')[1:]
        profile = response.css('div.pro_l_pht a img')[0]
        yield {
            'id': '{}-{}-{}'.format(self.name, id, 'profile'),
            'url': resolve(response, profile)
        }
