import urlparse

import scrapy

def get(element, attr):
    return element.xpath('./@{}'.format(attr)).extract()[0]

def resolve(response, image):
    return urlparse.urljoin(response.url, get(image, 'src'))

def get_value(response, key):
    query = urlparse.urlsplit(response.url).query
    return urlparse.parse_qs(query)[key][0]

class BeHappy2daySpider(scrapy.Spider):
    name = 'behappy2day'

    def start_requests(self):
        for i in range(30000, 31000):
            url = 'https://www.behappy2day.com/girls_info.php?i={}'.format(i)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        id = get_value(response, 'i')
        image = response.css('img.sp_menu_avatar')[0]
        url = resolve(response, image)
        yield {'id': id, 'url': url}
