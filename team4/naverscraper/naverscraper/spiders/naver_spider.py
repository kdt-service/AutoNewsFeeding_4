import scrapy
import pandas as pd
from naverscraper.items import NaverscraperItem
from datetime import datetime, timedelta
import time
import traceback
import re
from naverscraper.cleanser import cleansing


class NaverSpiderSpider(scrapy.Spider):
    name = "naver_spider"
    allowed_domains = ["news.naver.com"]
    start_urls = ["http://news.naver.com/"]

    CATEGORIES = {
        ('경제', 101) : {
            '금융' : '259',
            '증권' : '258',
            '산업/재계' : '261',
            '중기/벤처' : '771',
            '부동산' : '260',
            '글로벌 경제' : '262',
            '생활경제' : '310',
            '경제 일반' : '263'
        },
        ('IT/과학', 105) : {
            '모바일' : '731',
            '인터넷/SNS' : '226',
            '통신/뉴미디어' : '227',
            'IT 일반' : '230',
            '보안/해킹' : '732',
            '컴퓨터' : '283',
            '게임/리뷰' : '229',
            '과학 일반' : '228'
        }
    }
    URL_FORMAT = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1={}&sid2={}&date={}&page={}'

    def start_requests(self):
        nowdate = datetime.now().date()

        # 최근 크롤링 날짜 조회 -> 없으면 오늘부터
        try:
            with open('/home/ubuntu/workspace/team4/latest_date', 'r') as f:
                lastdate = pd.to_datetime(f.read().strip()).date()
            
        except:
            lastdate = nowdate
            pass

        # 크롤링 날짜 업데이트
        with open('/home/ubuntu/workspace/team4/latest_date', 'w') as f:
            f.write(nowdate.strftime('%Y%m%d'))

        # 마지막 날짜부터 오늘 날짜까지 크롤링하기 위해 dates 생성
        dates = pd.date_range(end=nowdate, start=lastdate).strftime('%Y%m%d').tolist()

        latest_url = {}
        previous_url = {}
        # 서브카테고리별 가장 최근에 가져온 url 조회
        try:
            with open('./latest_url.txt', 'r') as f:
                for line in f.readlines():
                    previous_url[line.split(' ')[0]] = line.split(' ')[-1].strip()
                    print(previous_url)
        except:
            pass    

        # 파일 초기화
        with open('./latest_url.txt', 'w') as f:
            f.write('')

        for main_ctg in self.CATEGORIES:
            main_name, main_id = main_ctg
            for sub_name, sub_id in self.CATEGORIES[main_ctg].items():
                previous_url.setdefault(sub_id, '')
                latest_url.setdefault(sub_id, '')
                for date in dates:
                    # 각 날짜별 1페이지 url을 target_url로 설정
                    target_url = self.URL_FORMAT.format(main_id, sub_id, date, 1)
                    
                    yield scrapy.Request(url=target_url, callback=self.parse_url, meta={
                        'page':1, 'urls':[], 'main_category':main_name, 'sub_category':sub_name, 'sub_id':sub_id, 'previous_url':previous_url[sub_id], 'latest_url':'', 'stop':0})

    def parse_url(self, response):
        if response.meta.pop('stop'):
            return
        urls = response.xpath('//*[@id="main_content"]/div[2]/ul/li/dl/dt[1]/a/@href').extract()
        stop = response.meta['previous_url'] in urls

        if response.meta.pop('urls') == urls:# 마지막 페이지의 다음 페이지
            return
        if response.meta['latest_url'] == '':
            response.meta['latest_url'] = urls[0]
            with open('./latest_url.txt', 'a') as f:
                f.write(response.meta.pop('sub_id')+' '+urls[0]+'\n')

        for url in urls:
            if response.meta['previous_url'] == url:
                return
            yield scrapy.Request(url=url, callback=self.parse, meta={**response.meta})
            #뉴스목록 페이지의 meta를 각 뉴스기사 페이지에 그대로전달 -> parse 안에서 위에서 설정해준 response.meta값 사용

        # 다음페이지
        page = response.meta.pop('page')# 현재 페이지 확인
        target_url = re.sub('page\=\d+', f'page={page+1}', response.url)# response의 url에서 page의 수 1 늘려줌
        yield scrapy.Request(url=target_url, callback=self.parse_url, meta={**response.meta, 'page':page+1, 'urls':urls, 'stop':stop})
        # 이전페이지, 마지막페이지 url비교하기 위해 urls도 meta로 넘김


    def parse(self, response):
        item = NaverscraperItem()
        item['id'] = response.url.split('/')[-2] + response.url.split('/')[-1][:10]
        item['platform'] = '네이버'
        item['main_category'] = response.meta['main_category']
        item['sub_category'] = response.meta['sub_category']
        item['title'] = response.xpath('//*[@id="title_area"]/span/text()').extract()
        try:
            item['writer'] = response.css('.byline_s::text').get().strip().split(' ')[0].split('(')[0].split(' ')[0]
        except:
            item['writer'] = None
        item['content'] = cleansing(' '.join(response.xpath('//*[@id="dic_area"]//text()').extract()), item['writer'])
        item['writed_at'] = response.css('.media_end_head_info_datestamp_time::attr(data-date-time)').get()
        item['link'] = response.url

        if item['title'] == []:
            with open('./error_urls', 'a') as f:
                f.write(response.url + '\n')
            return

        yield item
