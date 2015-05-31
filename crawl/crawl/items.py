from scrapy import Field, Item

class VideoItem(Item):
    url = Field()
    title = Field()
    description = Field()
