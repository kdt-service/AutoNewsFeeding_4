from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# scrapy 변수 설정, settings에서 데이터 이름, 형식 지정
SPIDER_NAME = 'naver_spider'

# scrapy crawler 실행하는 함수(크롤링 시 cleansing 적용하여 content에 저장)
def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(SPIDER_NAME)#, output_filename=OUTPUT_FILENAME, output_format=OUTPUT_FORMAT
    process.start()

if __name__=='__main__':
    run_spider()