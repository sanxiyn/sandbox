import urlparse

import scrapy

def get(element, attr):
    return element.xpath('./@{}'.format(attr)).extract()[0]

def resolve(response, image):
    return urlparse.urljoin(response.url, get(image, 'href'))

def get_value(response, key):
    query = urlparse.urlsplit(response.url).query
    return urlparse.parse_qs(query)[key][0]

class AnastasiaDateSpider(scrapy.Spider):
    name = 'anastasiadate'

    def start_requests(self):
        for i in range(1800000, 1801000):
            url = 'http://www.anastasiadate.com/pages/lady/profile/profilepreview.aspx?LadyID={}'.format(i)
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
