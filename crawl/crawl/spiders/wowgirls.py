from scrapy import Request, Spider

from crawl import items

def clean(text):
    text = text.replace(u'\N{EN DASH}', '--')
    text = text.replace(u'\N{RIGHT SINGLE QUOTATION MARK}', "'")
    text = text.replace(u'\N{HORIZONTAL ELLIPSIS}', '...')
    text = text.strip()
    return text

class WowGirlsSpider(Spider):
    name = 'wowgirls'

    def start_requests(self):
        for i in range(1, 11):
            url = 'http://wowgirls.tv/latest-videos/page/{}/'.format(i)
            yield Request(url, self.parse_page)

    def parse_page(self, response):
        for url in response.xpath('//h3/a/@href').extract():
            yield Request(url, self.parse_video)

    def parse_video(self, response):
        url = response.url
        title = response.xpath('//h1/text()').extract()[0]
        description = response.xpath('//p')[3]
        description = ''.join(description.xpath('.//text()').extract())
        title = clean(title)
        description = clean(description)
        yield items.VideoItem(url=url, title=title, description=description)
