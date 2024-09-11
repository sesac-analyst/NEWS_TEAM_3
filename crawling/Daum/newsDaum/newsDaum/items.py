# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
import scrapy

class NewsdaumItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # id = Field()
    platform = Field()
    category = Field()
    publisher = Field()
    title = Field()
    content = Field()
    editor = Field()
    change_date = Field()
    Url = Field()
    sticker = Field()

    
    pass
