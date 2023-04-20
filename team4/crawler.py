from multiprocessing import Pool
import time
import numpy as np
import  pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta

import re
from fake_useragent import UserAgent
import json

ua = UserAgent(verify_ssl=False)
fake_ua = ua.random

headers = {
    'user-agent' : fake_ua
}

category = {
  #경제
  '101' : ['258','259','260','261','262','263','310','771'],
  #IT/과학
  '105' : ['226','227','228','229','230','283','731','732']
}

# 코드 매칭
category_dict = {
    '101' : '경제',
    '105' : 'IT/과학',

    #경제
    '259' : '금융',
    '258' : '증권',
    '260' : '부동산',
    '261' : '산업/제계',
    '262' : '글로벌 경제',
    '263' : '경제일반',
    '310' : '생활경제',
    '771' : '중기/벤처',

    #IT/과학
    '226' : '인터넷/SNS',
    '227' : '통신/뉴미디어',
    '228' : '과학/일반',
    '229' : '게임/리뷰',
    '230' : 'IT일반',
    '283' : '컴퓨터',
    '731' : '모바일',
    '732' : '보안/해킹'   
}

start_time = time.time()

def check_new_content(url, recent_url):
    page = 1
    while True:
        contents_urls = getUrls(url+str(page))
        
        if recent_url in contents_urls:
            return url+str(page)
        
        page+=1
        

def getEndPage(url, recent_url):

    if recent_url:
        end_page_url = check_new_content(url, recent_url)

    else:
        end_page_url = f'{url}999'
        
    print(end_page_url)
    response = requests.get(end_page_url, headers=headers)
    soup = bs(response.text, "html.parser")

    return soup.select_one('#main_content > div.paging > strong').text
  

def getUrls(url):
  
  res = requests.get(url, headers=headers)

  if res.status_code != 200:
    print("page Request Error")
    return 
  
  soup = bs(res.text, "html.parser")
  now_urls =[]
  
  for row in soup.select('#main_content > div.list_body.newsflash_body > ul > li'):
      row = row.select_one('a')
      now_urls.append(row['href'])  
  
  return now_urls


def make_new_data():
    
    recent_urls = read_recent_urls()
    new_contents = pd.DataFrame()
    
    try:
        last_date = pd.to_datetime(recent_urls['last_date'])
    except:
        last_date = datetime(2023,4,19).date()
    today = pd.to_datetime(time.strftime('%Y%m%d', time.localtime())).date()
    num_cores = 8
    
    # 탐색할 날짜 리스트를 먼저 생성합니다.
    dates = [last_date]
    app_date = 1
    if last_date == today:
        app_date = 0
    while app_date:
        last_date = last_date + timedelta(days=1)
        dates.append(last_date)
        if last_date == today:
            break

    # 날짜 -> 카테고리1 -> 카테고리2
    for date in dates:
        detail_date = date.strftime('%Y%m%d') #  20230201 형태
        print(detail_date)
        for main, sub_lst in category.items(): # 카테고리1 : 경제, IT/과학
            for sub in sub_lst: # 카테고리2
                new_contents_sub = pd.DataFrame(columns=['main_category', 'sub_category', 'content', 'platform', 'source',
           'title', 'writed_at', 'writer','url'])

                url = f'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={sub}&sid1={main}&date={detail_date}&page='

                try:
                    recent_url = recent_urls[sub]
                except:
                    recent_url = ''

                print('recent_url : '+recent_url)

                new_contents_sub['url'] = get_content_url(url, recent_url)

                df_split = np.array_split(new_contents_sub, num_cores)

                pool = Pool(num_cores)
                new_contents_sub = pool.map(get_news_content, df_split)

                for contents in new_contents_sub[::-1]:
                    contents['main_category'] = category_dict[main]
                    contents['sub_category'] = category_dict[sub]
                    contents['platform'] = '네이버'
                    new_contents = pd.concat([contents, new_contents], axis=0)


                recent_urls[sub] = new_contents.iloc[0]['url']
                break
            break
        break
    return new_contents, recent_urls # news dataframe

def save_recent_urls(recent_urls):
    with open('./recent_urls.json','w') as f:
        json.dump(recent_urls, f, ensure_ascii=False, indent=4)


def read_recent_urls():
    recent_url = dict()
    try:
        with open('./recent_urls.json','r') as f:
            recent_url = json.load(f)
    except:
        print('Not exist recent_urls')
        
    return recent_url
        
        
def get_content_url(base_url, recent_url):
    
    pages = [base_url+str(i) for i in range(1, int(getEndPage(base_url, recent_url))+1)]
   
    urls = []
    
    for page_url in pages:
        urls += getUrls(page_url)
        
    if recent_url:
        urls = urls[:urls.index(recent_url)]
        
    return urls
    
def get_news_content(rows):
    for idx, row in rows.iterrows():
        url = row['url']
        response = requests.get(url, headers=headers)
        soup = bs(response.text, "html.parser")
        item = dict()
        try:
            row['title'] = soup.select_one('#title_area > span').text
        except:
            row['title'] = ''
        isWriter = soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_journalist > a > em')
        row['writer'] = isWriter.text if isWriter else ''
        row['content'] = soup.select_one('#newsct_article').text
        row['writed_at'] = soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span')['data-date-time']
        
    return rows

def load_crawled_contents(file_path):
    try:
        news = pd.read_csv(file_path, index_col=False)
        return news
    except:
        return pd.DataFrame()


def save_news_data(file_path, old, new):
    
    data = pd.concat([old,new])
    
    data.to_csv(file_path, index=False)

# 통합 클렌징 코드
def cleansing(text:str, writer:str=None) -> str:

    # 특수기호 제거
    text = re.sub('[▶△▶️◀️▷ⓒ■◆●©️]', '', text)
    # ·ㆍ■◆△▷▶▼�"'…※↑↓▲☞ⓒ⅔
    
    text = text.replace('“','"').replace('”','"')
    text = text.replace("‘","'").replace("’","'")

    # 인코딩오류 해결 (공백으로 치환)
    text = re.sub('[\xa0\u2008\u2190]', ' ', text)

    # URL제거를 위해 필요없는 문구 처리
    text = text.replace('https://', '')
    # 이메일 처리, URL 제거
    # '[\w\.-]+(\@|\.)[\w\.-]+\.[\w\.]+'
    text = re.sub('([\w\-]+(\@|\.)[\w\-.]+)', '', text)

    # 기자 제거
    # [~~~ 이데일리 ~~ 기자 ~~~]
    if writer:
        left_s, right_s, not_left, not_right = ('[\(\{\[\<]', '[\)\}\]\>]', '[^\(\{\[\<]', '[^\)\}\]\>]')
        text = re.sub('%s%s+%s%s+?%s'%(left_s, not_right, writer, not_left, right_s), '', text)

    # ., 공백, 줄바꿈 여러개 제거 
    # \s -> 공백( ), 탭(\t), 줄바꿈(\n)
    text = re.sub('[\.]{2,}', '.', text)
    text = re.sub('[\t]+', ' ', text)
    text = re.sub('[ ]{2,}', ' ', text)
    text = re.sub('[\n]{2,}', '\n', text)

    return text

if __name__ == '__main__':
    # 함수형 프로그래밍
    crawled_contents = load_crawled_contents('./news.csv')
    new_contents, recent_urls = make_new_data()

    last_date = new_contents['writed_at'].sort_values().dropna().iloc[-1]
    recent_urls['last_date'] = last_date
    
    # cleaning
    new_contents['content'] = new_contents['content'].apply(cleansing)
    
    print(f'New Content {len(new_contents)}')
    save_recent_urls(recent_urls)
    
    # saving the csv file with utf-8 encoding
    crawled_contents.to_csv('./news.csv', index=False, encoding='utf-8-sig')
    new_contents.to_csv('./news.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
