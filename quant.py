import pandas as pd
import pandas_datareader as pdr
import numpy as np
import datetime
import FinanceDataReader as fdr

# 코스피와 코스닥 종목 코드 가져오기
kospi = fdr.StockListing('KOSPI') # 코스피
kosdaq = fdr.StockListing('KOSDAQ') # 코스닥

total = pd.concat([kospi, kosdaq])
codes = total['Code']

print('종목 정보 로드 완료')

passed_codes = []

for code in codes:
    try:
        # 주가 데이터 가져오기
        stock = pdr.naver.NaverDailyReader(code, start=(datetime.datetime.now()-datetime.timedelta(days=365*2)).strftime('%Y%m%d')).read()
        stock['Open'] = pd.to_numeric(stock['Open'], errors='coerce')
        stock['High'] = pd.to_numeric(stock['High'], errors='coerce')
        stock['Low'] = pd.to_numeric(stock['Low'], errors='coerce')
        stock['Close'] = pd.to_numeric(stock['Close'], errors='coerce')
        stock['Volume'] = pd.to_numeric(stock['Volume'], errors='coerce')

        # 조건 1: 오늘의 종가가 20일, 60일, 120일 이동평균선 위에 있는지 확인
        stock['MA20'] = stock['Close'].rolling(window=20).mean()
        stock['MA60'] = stock['Close'].rolling(window=60).mean()
        stock['MA120'] = stock['Close'].rolling(window=120).mean()
        condition1 = all(stock.iloc[-1]['Close'] > stock.iloc[-1][ma] for ma in ['MA20', 'MA60', 'MA120'])

        # 조건 2: 최근 1주일의 평균 거래량이 이전 1년 동안의 평균 거래량의 2배 이상인지 확인
        avg_volume_last_year = stock.iloc[:-7]['Volume'].mean()
        avg_volume_last_week = stock.iloc[-7:]['Volume'].mean()
        condition2 = avg_volume_last_week > 2 * avg_volume_last_year

        # 조건 3: 현재 종가가 2년 전의 종가의 30% 이상 하락한 경우
        condition3 = stock.iloc[-1]['Close'] < 0.7 * stock.iloc[0]['Close']

        # 세 가지 조건을 모두 만족하는지 확인
        if condition1 and condition2 and condition3:
            passed_codes.append(code)
            print(code)
    except Exception as e:
        print(f"Error occurred with code {code}: {str(e)}")
        
# 조건을 만족하는 종목 코드 출력
find = total.set_index('Code')
print("Passed codes:", passed_codes)
for code in passed_codes:
    print(f"Code: {code}, Name: {find.loc[code, 'Name']}")
