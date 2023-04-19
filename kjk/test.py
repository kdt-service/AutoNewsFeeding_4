from konlpy.tag import Mecab
from gensim.summarization import summarize

sen = '안녕하세요. 테스트 중입니다.'
article = '지난해 하반기 월급여가 400만원이 넘는 근로자의 비중이 처음으로 20% 대를 넘어선 역대 최고치를 나타냈다. 반면 월급여가 200만원이 채 되지 않는 근로자 비율은 통계 작성 이래 가장 낮은 수준을 보였다. 통계청이 18일 발표한 2022년 하반기 지역별 고용조사 자료에 따르면, 지난해 10월 임금 근로자 총 2168만4000명 중 월 400만원 이상을 받은 근로자 수는 478만4000명으로 전체의 22.1%를 차지했다. 이는 관련 통계가 작성된 2013년 하반기 이후 가장 높은 수치다. 월급여란 최근 3개월 동안 받은 각종 상여금 및 현물을 포함한 총 수령액(세금 공제 전)의 평균치를 뜻한다.'
mecab = Mecab('/home/ubuntu/anaconda3/envs/news4/lib/mecab/dic/mecab-ko-dic')
tokens = mecab.pos(sen)

print('test')
print(tokens)
print(summarize(article, word_count=20))