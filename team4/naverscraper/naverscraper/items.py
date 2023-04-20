# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NaverscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    platform = scrapy.Field()
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    writer = scrapy.Field()
    writed_at = scrapy.Field()
    link = scrapy.Field()
    pass
