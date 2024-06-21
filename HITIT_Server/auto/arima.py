import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 파일의 경로
parent_dir = os.path.dirname(current_dir) # 상위 디렉터리 경로
sys.path.append(parent_dir) # 상위 디렉터리를 sys.path에 추가

# MYSQL 연결
from mysqlconnect import connect_to_mysql
connection = connect_to_mysql()
cursor = connection.cursor()

#종목 분석할 종목들 불러오기(펀드 코드)
cursor.execute("select fund_code from fund_products_4 where (DATE(arima_update) IS NULL OR DATE(arima_update) <> DATE(NOW()))")
codes = cursor.fetchall()
codes = [ elem[0] for elem in codes]

from arima_func import get_arima_predict

for code in codes:
    print(f"{codes.index(code)+1}/{len(codes)}", code)
    
    # {'예측값': 14925.268709016453, '예측일': '20240718', '등락률': 5.19} 이런식으로 예측 들어온다
    result = get_arima_predict(code, kind = "fund")
    
    print(result)
    if result.get('error', False):
        print(f"에러발생, {code}")
        continue
    
    predicted_price, percent = result['예측값'], result['등락률']
    # query = f"insert into fund_products_4 (fund_code, arima_price, arima_percent, arima_update) values ('{code}',{predicted_price},{percent},NOW())"
    query = f"""
    UPDATE fund_products_4
    SET arima_price = {predicted_price},
        arima_percent = {percent},
        arima_update = NOW()
    WHERE fund_code = '{code}'
        AND (DATE(arima_update) IS NULL OR DATE(arima_update) <> NOW());
    """
    # cursor.execute(query)
    
    if cursor.rowcount == 0:
        print(f"No rows updated for fund code {code}")
    else:
        print(f"Updated {cursor.rowcount} rows for fund code {code}")
        
    connection.commit()
