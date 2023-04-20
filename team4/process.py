import numpy as np
import pandas as pd
from datetime import datetime
import csv

from konlpy.tag import Mecab
from gensim.summarization import summarize

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('현재 경로:', os.path.abspath('.'))

data_path = '/home/ubuntu/workspace/team4/naverscraper/naverscraper/test.csv'

# 불용어 불러오기
stopword_file = open('./stopword.txt', 'r', encoding='utf-8')
stopwords= []
for word in stopword_file.readlines():
    stopwords.append(word.rstrip())
stopword_file.close()

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

# 크롤링한 데이터 불러오는 함수
def load_data(path):
    data = pd.read_csv(path, encoding='utf-8', dtype=object)
    # print(data.groupby(by=['main_category', 'sub_category']).id.count())
    return data

def del_data(path):
    # test.csv를 삭제
    return

# 추출한 기사 데이터 csv 파일로 저장하는 함수
def save_articles(article_info_list):
    fname = ['category', 'title', 'link', 'summary']
    with open('./articles.csv', 'w') as f:
        w = csv.DictWriter(f, fieldnames=fname)
        w.writeheader()
        w.writerows(article_info_list)
        return
    
# 사망기사 관련 키워드 두 개 이상 포함 시 삭제  
def isObituary(text):
    words = ['별세', '장례', '발인', '부고', '친상']
    count = 0
    for word in words:
        if word in text:
            count += 1
            if count > 1:
                return True
    return False

# 주어진 길이보다 긴 경우 True 반환
def isLonger(text, length):
    if len(text) > length:
        return True
    else:
        return False

def mecab_tokenizer(doc):
    mecab = Mecab('/home/ubuntu/anaconda3/envs/news4/lib/mecab/dic/mecab-ko-dic')
    sentences = [sentences.strip() for sentences in doc.split('.')]
    pos_list = []
    for sent in sentences:
        for pos in mecab.pos(sent):
            if pos[1][0] in ['N']: # 우선 명사만 토큰화 
                if len(pos[0]) > 1:
                    if pos[0] not in stopwords:
                        pos_list.append(pos[0])
    return ' '.join(pos_list)

# 데이터를 전처리하는 함수
def preprocess(data):
    print('처리 전 기사 수 :', len(data))
    data.dropna(subset=['content'], inplace=True)
    data.drop_duplicates(subset=['title', 'writer'], keep='first', inplace=True)
    data.drop_duplicates(subset=['title', 'content'], keep='first', inplace=True)
    data = data[data.content.apply(isLonger, args=[150])]
    data = data[~data.content.apply(isObituary)]
    data = data[~data.title.str.contains('\[인사\]')]
    data = data[~data.title.str.contains('\[.*부고.*\]')]
    data = data[~data.title.str.contains('\[포토뉴스\]')]
    data = data[~data.title.str.contains('코스피') | data.content.apply(isLonger, args=[300])]
    data = data[~data.title.str.contains('증시') | data.content.apply(isLonger, args=[300])]
    print('처리 후 기사 수 :', len(data))
    data['tokens'] = data.content.apply(mecab_tokenizer)
    return data

def find_best_lda(train_data, n_jobs=-1):
    lda_pipeline = Pipeline([
        ('tfidf_vect', TfidfVectorizer(max_df=.9, min_df=2, lowercase=False, use_idf=False)),
        ('lda', LatentDirichletAllocation(max_iter=10, random_state=0, learning_method='online'))
    ])
    search_params = {
        'tfidf_vect__max_features' : [500, 700, 1000],
        'tfidf_vect__ngram_range' : [(1,1), (1,2)],
        'lda__n_components' : [3, 5, 10]
    }
    gs_lda = GridSearchCV(lda_pipeline, param_grid=search_params, n_jobs=n_jobs)
    gs_lda = gs_lda.fit(train_data)

    return gs_lda.best_estimator_

# lda의 토픽별 문서 인덱스가 담긴 리스트 반환
def get_idxs_by_topic(model, train_data, threshold=0.5):
    doc_topic_matrix = model.transform(train_data)
    idxs_by_topic = []
    for i in range(model.get_params()['lda__n_components']):
        idxs = []
        for j, doc in enumerate(doc_topic_matrix):
            max_topic = np.argmax(doc)
            max_prob = doc[max_topic]
            if max_topic == i and max_prob >= threshold:
                idxs.append(j)
        idxs_by_topic.append(idxs)
    return idxs_by_topic

# 서브카테고리별 가장 많이 나타난 토픽에 대한 상위기사 k개를 찾아 딕셔너리 형태로 반환
def top_articles_by_category(preprocessed_data, k=1):
    print(datetime.now().strftime('%H:%M:%S')+' 카테고리별 기사 추출 시작')
    SUB_CATEGORIES = [] # 서브카테고리 목록
    top_articles = []   # 서브카테고리별 대표기사의 제목과 url, 요약
    for main_category in CATEGORIES:
        for sub_category in CATEGORIES[main_category].items():
            SUB_CATEGORIES.append(sub_category[0])

    for sub_category in SUB_CATEGORIES:
        category_data = preprocessed_data[preprocessed_data.sub_category==sub_category]
        category_content = category_data.content.values
        category_tokens = category_data.tokens.values
        # 파라미터 튜닝, 토픽 개수 저장
        best_model = find_best_lda(category_tokens)
        number_of_topic = best_model.get_params()['lda__n_components']

        # 토픽별 인덱스 리스트를 가져와 가장 많이 나타난 토픽의 인덱스 찾기
        idxs_by_topic = get_idxs_by_topic(best_model, category_tokens, 0.6)
        topic_count = list(map(len, idxs_by_topic))
        most_topic = np.argmax(topic_count)

        # lda 점수가 가장 높은 문서 찾아 제목과 url 저장
        most_topic_weights = best_model.transform(category_tokens)[:, most_topic]
        top_doc_idx = np.argsort(most_topic_weights)[::-1][:k]
        for idx in top_doc_idx:
            top_articles.append({
                                'category' : sub_category,
                                'title' : category_data.title.values[idx],
                                'link' : category_data.link.values[idx],
                                'summary' : summarize(category_content[idx], word_count=20, ratio=.2)
            })
        print(datetime.now().strftime('%H:%M:%S'), sub_category, '추출 완료')

    return top_articles

def process():
    data = load_data(data_path)
    preprocessed_data = preprocess(data)
    print(preprocessed_data.groupby(by=['main_category', 'sub_category']).id.count())
    top_article = top_articles_by_category(preprocessed_data, 1)
    save_articles(top_article)
    return 

if __name__=='__main__':
    process()