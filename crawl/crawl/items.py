from scrapy import Field, Item

class VideoItem(Item):
    url = Field()
    title = Field()
    description = Field()

class WhoDocumentItem(Item):
    url = Field()
    language = Field()
    title = Field()
