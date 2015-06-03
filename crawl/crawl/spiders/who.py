import urlparse

from scrapy import Request, Spider

from crawl import items

def get(element, attr):
    return element.xpath('./@{}'.format(attr)).extract()[0]

def text(element):
    return element.xpath('./text()').extract()[0]

def resolve(response, link):
    return urlparse.urljoin(response.url, get(link, 'href'))

def remove_suffix(suffix, s):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s

class WhoSpider(Spider):
    name = 'who'

    def start_requests(self):
        url = 'http://who.int/mediacentre/news/releases/previous/en'
        yield Request('{}/index.html'.format(url), self.parse_year)
        for i in range(1, 8):
            yield Request('{}/index{}.html'.format(url, i), self.parse_year)

    def parse_year(self, response):
        for link in response.css('.auto_archive a'):
            yield Request(resolve(response, link), self.parse_news)

    def parse_news(self, response):
        for item in self.parse_news_language(response):
            yield item
        for language in response.css('#language .item'):
            cls = get(language, 'class')
            if 'selected' in cls:
                continue
            if 'disabled' in cls:
                continue
            link = language.css('a')[0]
            yield Request(resolve(response, link), self.parse_news_language)

    def parse_news_language(self, response):
        url = response.url
        for language in 'ar en es fr ru zh'.split():
            language_path = '/{}/'.format(language)
            if language_path in url:
                break
        url = remove_suffix(language_path, url)
        title = text(response.css('h1')[0])
        yield items.WhoDocumentItem(url=url, language=language, title=title)
