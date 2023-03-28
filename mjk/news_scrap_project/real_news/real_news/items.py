# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RealNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # newsid = scrapy.Field()
    platform = scrapy.Field()
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field() 
    writer = scrapy.Field() 
    writed_at = scrapy.Field() #writed_at 형식 : 2023-03-17 16:30:45
    
