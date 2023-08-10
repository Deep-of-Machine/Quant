from pykrx import stock
import datetime
import FinanceDataReader as fdr
import pandas as pd


kospi = fdr.StockListing('KOSPI') # 코스피
kosdaq = fdr.StockListing('KOSDAQ') # 코스닥
total = pd.concat([kospi, kosdaq])
codes = total['Code']

print('종목 정보 로드 완료')

results = []


try:
    for code in codes:
        positive_days = 0
        for i in range(5):
            date_str = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y%m%d')
            df = stock.get_market_trading_value_by_investor(date_str, date_str, ticker=code)
            foreign_net_buy = df.loc["외국인", "순매수"]
            institution_net_buy = df.loc["기관합계", "순매수"]

            if foreign_net_buy > 0 and institution_net_buy > 0:
                positive_days += 1
            
        if positive_days == 5:
            results.append(code)
            print(code)
except Exception as e:
    print(f"Error occurred with code {code}: {str(e)}")
    
print(results)