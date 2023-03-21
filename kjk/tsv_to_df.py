import pandas as pd

def get_contents(id):
    return open('Naver_news/news_contents/'+id+'.txt', 'r', encoding='utf-8').read()

def get_df():
    df = pd.read_csv('Naver_news/metadata.tsv', sep='\t')
    df['content'] = df.apply(lambda x:get_contents(x['id']), axis=1)
    return df

if __name__ == '__main__':
    get_df()