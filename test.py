import pandas as pd
import pandas_datareader as pdr
import datetime
import FinanceDataReader as fdr
from concurrent.futures import ProcessPoolExecutor

def check_conditions(code):
    try:
        # 주가 데이터 가져오기
        stock = pdr.naver.NaverDailyReader(code, start=(datetime.datetime.now() - datetime.timedelta(days=365*2)).strftime('%Y%m%d')).read()
        stock['Open'] = pd.to_numeric(stock['Open'], errors='coerce')
        stock['High'] = pd.to_numeric(stock['High'], errors='coerce')
        stock['Low'] = pd.to_numeric(stock['Low'], errors='coerce')
        stock['Close'] = pd.to_numeric(stock['Close'], errors='coerce')
        stock['Volume'] = pd.to_numeric(stock['Volume'], errors='coerce')

        # 조건 1: 현재 종가가 2년 전의 종가의 50% 이하로 하락
        condition1 = stock.iloc[-1]['Close'] < 0.5 * stock.iloc[0]['Close']

        # 조건 2: 최근 1주일의 거래량 평균이 최근 6개월의 거래량 평균보다 100% 이상 증가
        avg_volume_last_six_months = stock.iloc[-180:-7]['Volume'].mean()
        avg_volume_last_week = stock.iloc[-7:]['Volume'].mean()
        condition2 = avg_volume_last_week > 2 * avg_volume_last_six_months

        # 조건 3: 시가 총액이 2000억 이상
        # condition3 = total.loc[code, 'MarketCap'] >= 200000000000

        # 조건 4: 현재 종가가 20일 이동평균선 위
        stock['MA20'] = stock['Close'].rolling(window=20).mean()
        condition4 = stock.iloc[-1]['Close'] > stock.iloc[-1]['MA20']

        # 모든 조건을 만족하는지 확인
        if condition1 and condition2 and condition4:
            print(code)
            return code
    except Exception as e:
        print(f"Error occurred with code {code}: {str(e)}")
    return None

def main():
    # 코스피와 코스닥 종목 코드 가져오기
    global total  # 전역 변수로 선언
    kospi = fdr.StockListing('KOSPI')
    kosdaq = fdr.StockListing('KOSDAQ')
    total = pd.concat([kospi, kosdaq])
    codes = total['Code']

    print('종목 정보 로드 완료')

    # 병렬 처리로 종목 데이터 다운로드 및 조건 체크
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(check_conditions, codes))

    # 결과 필터링
    passed_codes = [code for code in results if code]

    # 조건을 만족하는 종목 코드 출력
    find = total.set_index('Code')
    print("Passed codes:", passed_codes)
    for code in passed_codes:
        print(f"Code: {code}, Name: {find.loc[code, 'Name']}")

if __name__ == '__main__':
    main()
