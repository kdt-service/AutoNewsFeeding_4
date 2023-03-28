import scrapy
from real_news.items import RealNewsItem
import re

#parameters organize
#날짜
date_list = list(range(20230201, 20230229)) + list(range(20230301, 20230317))
#대분류
main_categories = {'105' : 'IT/과학'} #'101' : '경제', 
#소분류
sub_categories = {
    # #경제
    # '259' : '금융',
    # '258' : '증권',
    # '260' : '부동산',
    # '261' : '산업/제계',
    # '262' : '글로벌 경제',
    # '263' : '경제일반',
    # '310' : '생활경제',
    # '771' : '중기/벤처',

    # #IT/과학
    '226' : '인터넷/SNS',
    '227' : '통신/뉴미디어',
    '228' : '과학/일반',
    '229' : '게임/리뷰',
    '230' : 'IT일반',
    '283' : '컴퓨터',
    '731' : '모바일',
    '732' : '보안/해킹'
    }




class NavercrawlerSpider(scrapy.Spider):
    name = "navercrawler"
    allowed_domains = ["news.naver.com"]
    start_urls = ["http://news.naver.com/"]
    
    def start_requests(self):
        #처음 시작하는 URL 만들어주기
        #url parsing(날짜, 대분류, 소분류까지만. 페이지는 아직 X)
        page_urls = []
        for date in date_list:
            for main_category in main_categories:
                for sub_category in sub_categories:
                    page_url = f'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={sub_category}&sid1={main_category}&date={date}&page=1'
                    page_urls.append(page_url)
                    yield scrapy.Request(page_url, callback=self.news_url_parser,  meta = {'page' : 1, 'main' : main_category, 'urls' : [], 'sub' : sub_category})

       
    def news_url_parser(self, response):
        #페이지 URL마다 뉴스기사 가져오기
        urls = list(set(response.css('li dt a::attr(href)').extract()))
        
        if response.meta.pop('urls') == urls:
            return
        
        for url in urls:
            yield scrapy.Request(url, self.parse, meta={**response.meta})
        
        page = response.meta.pop('page')
        target_url = re.sub('page\=\d+', f'page={page+1}', response.url)
        
        
        
        yield scrapy.Request(url=target_url, callback=self.news_url_parser, meta={**response.meta, 'page': page+1, 'urls':urls})



    def parse(self, response):
        item = RealNewsItem()
        
        # item['newsid'] = response.css()
        item['platform'] = 'naver'
        item['main_category'] = 'IT/과학'      #main_categories[response.meta.pop('main')]
        item['sub_category'] = sub_categories[response.meta.pop('sub')]
        item['title'] = response.xpath('//*[@id="title_area"]/span/text()').extract()
        item['content'] = response.xpath('//*[@id="dic_area"]/text()').extract()
        item['writer'] = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[2]/a/em').extract()
        item['writed_at'] = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div/span/text()').extract()[0].split()[0]
        
        yield item
