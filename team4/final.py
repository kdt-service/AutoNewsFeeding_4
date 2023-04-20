#프로그램 RUN
import smtplib
import email
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('현재 경로:', os.path.abspath('.'))

#SMTP 로그인
def login_send():
    SMTP_SERVER = 'smtp.naver.com'
    SMTP_PORT = 465
    SMTP_USER = 'dev_news@naver.com'
    SMTP_PASSWORD = open('./pw_config', 'r').read().strip()
    subscribers(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
    
    return


#구독자 정보 불러오기
def subscribers(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD):
    to_users = pd.read_csv('./subscribers.csv')['subscribers'].values.tolist()
    target_addr = ','.join(to_users)
    subject = datetime.today().strftime("[DEV_NEWS] %Y년 %m월 %d일, 오늘의 개발자 뉴스 요약입니다.")
    
    f = open('./frame.html')
    contents = f.read()
    contents = htmledit(contents)
    
    msg = MIMEMultipart('alternative')
    msg['From'] = "DEVELOPERS NEWSTODAY<dev_news@naver.com>"
    msg['To'] = target_addr
    msg['Subject'] = subject
    text = MIMEText(contents, 'html')
    msg.attach(text)
    
    smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    smtp.login(SMTP_USER, SMTP_PASSWORD)
    smtp.sendmail(SMTP_USER, to_users, msg.as_string())
    smtp.close()
    return

def htmledit(contents):
    
    
    
    
    
    #날짜 변경
    today_date = datetime.today().strftime("%Y년 %m월 %d일")
    contents = contents.replace('today_date', today_date)
    #최종 결과물 csv 가져오기
    articles = pd.read_csv('./articles.csv')

    
    #헤더 꾸미기
    
    
    
    
    #링크 replace
    contents = contents.replace('금융링크', articles['link'][0])
    contents = contents.replace('증권링크', articles['link'][1])
    contents = contents.replace('산업링크', articles['link'][2])
    contents = contents.replace('중기링크', articles['link'][3])
    contents = contents.replace('부동산링', articles['link'][4])
    contents = contents.replace('글경링크', articles['link'][5])
    contents = contents.replace('생경링크', articles['link'][6])
    contents = contents.replace('경제링크', articles['link'][7])
    
    contents = contents.replace('모바일링', articles['link'][8])
    contents = contents.replace('인터넷링', articles['link'][9])
    contents = contents.replace('통신뉴링', articles['link'][10])
    contents = contents.replace('IT링크', articles['link'][11])
    contents = contents.replace('보안링크', articles['link'][12])
    contents = contents.replace('컴퓨터링', articles['link'][13])
    contents = contents.replace('게임링크', articles['link'][14])
    contents = contents.replace('과학링크', articles['link'][15])
    
    #기사제목 가져오기
    contents = contents.replace('{금융기사제목}', articles['title'][0])
    contents = contents.replace('{증권기사제목}', articles['title'][1])
    contents = contents.replace('{산업기사제목}', articles['title'][2])
    contents = contents.replace('{중기기사제목}', articles['title'][3])
    contents = contents.replace('{부동산기사제목}', articles['title'][4])
    contents = contents.replace('{글경기사제목}', articles['title'][5])
    contents = contents.replace('{생활기사제목}', articles['title'][6])
    contents = contents.replace('{일반기사제목}', articles['title'][7])
    
    contents = contents.replace('{모바일기사제목}', articles['title'][8])
    contents = contents.replace('{인터넷기사제목}', articles['title'][9])
    contents = contents.replace('{통신기사제목}', articles['title'][10])
    contents = contents.replace('{IT기사제목}', articles['title'][11])
    contents = contents.replace('{보안기사제목}', articles['title'][12])
    contents = contents.replace('{컴퓨터기사제목}', articles['title'][13])
    contents = contents.replace('{게임기사제목}', articles['title'][14])
    contents = contents.replace('{과학기사제목}', articles['title'][15])
    
    #기사요약 가져오기
    contents = contents.replace('{금융기사요약}', articles['summary'][0])
    contents = contents.replace('{증권기사요약}', articles['summary'][1])
    contents = contents.replace('{산업기사요약}', articles['summary'][2])
    contents = contents.replace('{중기기사요약}', articles['summary'][3])
    contents = contents.replace('{부동산기사요약}', articles['summary'][4])
    contents = contents.replace('{글경기사요약}', articles['summary'][5])
    contents = contents.replace('{생활기사요약}', articles['summary'][6])
    contents = contents.replace('{일반기사요약}', articles['summary'][7])
    
    contents = contents.replace('{모바일기사요약}', articles['summary'][8])
    contents = contents.replace('{인터넷기사요약}', articles['summary'][9])
    contents = contents.replace('{통신기사요약}', articles['summary'][10])
    contents = contents.replace('{IT기사요약}', articles['summary'][11])
    contents = contents.replace('{보안기사요약}', articles['summary'][12])
    contents = contents.replace('{컴퓨터기사요약}', articles['summary'][13])
    contents = contents.replace('{게임기사요약}', articles['summary'][14])
    contents = contents.replace('{과학기사요약}', articles['summary'][15])
    
    
    
    
    
    
    
    
    
    
    
    
    return contents

if __name__=='__main__':
    login_send()