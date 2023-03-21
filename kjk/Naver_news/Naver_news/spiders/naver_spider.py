import scrapy
from Naver_news.items import NaverNewsItem
from datetime import datetime, timedelta
import traceback
import re

class NaverSpiderSpider(scrapy.Spider):
    name = "naver_spider"
    allowed_domains = ["news.naver.com"]
    start_urls = ["http://news.naver.com/"]

    CATEGORIES = {#경제(259, 258, 261, 771, 260, 262, 310, 263), IT/과학(731, 226, 227, 230, 732, 283, 229, 228)
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

    URL_FORMAT = 'https://news.naver.com/main/list.naver?mode=L2SD&mid=shm&sid1={}&sid2={}&date={}&listType=title&page={}'
    def start_requests(self):
        # 날짜리스트 생성(시작일부터 종료일까지)
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2023, 3, 16)
        dates = [start_date]
        while True:
            start_date = start_date + timedelta(days=1)
            dates.append(start_date)
            if start_date == end_date:
                break

        for main_ctg in self.CATEGORIES:
            main_name, main_id = main_ctg
            for sub_name, sub_id in self.CATEGORIES[main_ctg].items():
                for date in dates:
                    # 각 날짜별 1페이지 url을 target_url로 설정
                    target_url = self.URL_FORMAT.format(main_id, sub_id, date.strftime('%Y%m%d'), 1)

                    yield scrapy.Request(url=target_url, callback=self.parse_url, meta={
                        'page':1, 'urls':[], 'main_category':main_name, 'sub_category':sub_name})
                    
    def parse_url(self, response):
        urls = response.css('.type02 li a::attr(href)').getall()
        if response.meta.pop('urls') == urls:# 마지막 페이지의 다음 페이지
            return
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={**response.meta})

        # 다음페이지
        page = response.meta.pop('page')# 현재 페이지 확인
        target_url = re.sub('page\=\d+', f'page={page+1}', response.url)# response의 url에서 page의 수 1 늘려줌
        yield scrapy.Request(url=target_url, callback=self.parse_url, meta={**response.meta, 'page':page+1, 'urls':urls})
        # 이전페이지, 마지막페이지 url비교하기 위해 urls도 meta로 넘김
        
    def parse(self, response):
        try:
            id = response.url.split('/')[-1][:10]
            platform = '네이버'
            main_category = response.meta['sub_category']
            sub_category = response.meta['main_category']
            title = response.css('#title_area span::text').get().strip()
            content = response.css('#dic_area')[0].xpath('string(.)').extract()[0].strip()
            try:
                writer = response.css('.byline_s::text').get().strip().split(' ')[0].split('(')[0].split(' ')[0]
            except:
                writer = ''
            writed_at = response.css('.media_end_head_info_datestamp_time::attr(data-date-time)').get()
            link = response.url
            like = response.css('.u_likeit_text::text').get().strip()
            comment = response.css('#comment_count::text').get().strip()
            if like == '추천':
                like = '0'
            else:
                pass
            if comment == '댓글':
                comment = '0'
            else:
                pass

            with open('./news_contents/'+id+'.txt', 'w', encoding='utf-8') as f:
                f.write(content)

            datas = [id, platform, main_category, sub_category, title, writer, writed_at, link, like, comment]

            with open('./meta_data.tsv', 'a', encoding='utf-8') as f:
                f.write('\t'.join(map(str, datas)) + '\n')
            
        except:
            traceback.print_exc()
            with open('error_urls', 'a') as f:
                f.write(response.url + '\n')