import pandas as pd
import re

def cleansingData(path):
    data = pd.read_csv(path, dtype=object, encoding='utf-8')
    print('데이터 불러오기 완료 :', len(data))

    # 순서대로 \', 이메일, url, <>, [], (), 숫자, @~, ⓒ~, XXX 기자 제거
    regex = r'\\\''+'|'+r'\w+\@\w+\.\w+(\.\w{2})?'+'|'+r'(https?\:\/?\/?)?[가-힣\w\-]+\.[가-힣\w]+[^\s]*'+'|'+r'\<((?!\<).)*\>'+'|'+r'\[((?!\[).)*\]'+'|'+r'\(((?!\().)*\)'+'|'+r'\d+((?! ).)* ?원?'+'|'+r'[ⓒ@]((?! ).)*'+'|'+r'[가-힣]{3} ?기자'
    data['content'] = data['content'].apply(lambda x: re.sub(regex, '', x))
    data['content'] = data['content'].apply(lambda x: x.replace('\n', '').replace('\t', '').replace('\xa0', ''))    # \n, \t, \xa0 제거
    data['content'] = data['content'].apply(lambda x: re.sub(r'[^가-힣\w\.\,\'\"\` ]', ' ', x))                      # 한글, 영어, 온점, 콤마, 공백 제외한 문자 공백으로 대체
    # data['content'] = data['content'].apply(lambda x: re.sub(r'[\s]', '', x))
    data['content'] = data['content'].apply(lambda x: re.sub(r'(?<=[가-힣\w\.\,])  +(?=[가-힣\w\.\,])', ' ', x))    # 둘 이상 공백 있는 경우 하나의 공백으로 대체
    data['content'] = data['content'].apply(lambda x: x.strip())

    return data

PATH = './data.csv'

if __name__ == '__main__':
    cleansingData(PATH)
    pass