# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum
from scrapy.loader.processors import TakeFirst

class Original(Enum):
    huxiu  = 1
    kr     = 2

class Type(Enum):
    tech = 1
    life = 2
    business = 3

class Article(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    time = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    original =scrapy.Field(output_processor=TakeFirst())
    content = scrapy.Field(output_processor=TakeFirst())