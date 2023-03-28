from pathlib import Path

import scrapy


class NewsCrawlerSpider(scrapy.Spider):
    name = "newscrawler"

    def start_requests(self):
        sub_category_params = [731, 226, 227, 230, 732, 283, 229, 228]
        day_params = list(range(20230201, 20230229)) + list(range(20230301, 20230317))
        urls = []
        for i in sub_category_params:
            for day in day_params:
                n = 1
                url = f'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={i}&sid1=105&date={day}&page={n}'
                
                urls.append(url)
                
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = f'quotes-{page}.html'
        # Path(filename).write_bytes(response.body)
        # self.log(f'Saved file {filename}')
        
        
        
        
        # #items.py
        # id = scrapy.Field()
        # platform = scrapy.Field()
        # main_category = scrapy.Field()
        # sub_category = scrapy.Field()
        # title = scrapy.Field()
        # content = scrapy.Field() 
        # writer = scrapy.Field() 
        # writed_at = scrapy.Field() #writed_at 형식 : 2023-03-17 16:30:45