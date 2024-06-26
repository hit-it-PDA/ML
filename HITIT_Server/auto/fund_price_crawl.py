import requests
from datetime import datetime, timedelta
import requests
import sys
import os
import pandas as pd

# 현재 날짜 가져오기
today = datetime.now() 

# 날짜를 YYYYMMDD 형식으로 변환
today_str = today.strftime('%Y-%m-%d')
one_year_ago = today - timedelta(days=365)
one_year_ago_str = one_year_ago.strftime('%Y%m%d')
print(today_str,one_year_ago_str)

project_root = '/home/ubuntu/code/DE_ML/HITIT_Server'

sys.path.append(project_root)
from flask_server.utils.sql.sqlconnect import get_sql_connection

connection = get_sql_connection()

cursor = connection.cursor()

def fund_price_crawl(code) :
    print(f"code : {code} , {codes.index(code)}/{len(codes)}")
    global df
    df = pd.DataFrame()
    price_data = []
    results = []
    for page in range(1,2):
        url = f"https://www.fundguide.net/Api/Fund/GetFundRateGrid?fund_cd={code}&term_gb=12&time_gb=3&page_no={page}&row_cnt=10&_=1718757991716"
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        data = response.json()['Data'][0]
        price_data.extend(data)
    # print(price_data)
    for elem in price_data[:3]:
        # print(elem)
        date, price = elem['TRD_DT'], elem['STD_PRC']
        date = date.replace(".","-")
        # print(date)
        query = f"""INSERT INTO fund_prices (fund_code, Date, price) VALUES ('{code}', '{date}', {str(price).replace(",","")})"""
        # print(query)
        # if date != '2024-06-21':
        #     continue
        try : 
            cursor.execute(query)
            print(f"insert Success {code} : {date} ")
            print(query)
        except :
            print("failed insert")
        connection.commit()
        print(date)
        date1 = datetime.strptime(date.replace("-","."), '%Y.%m.%d')
        if date1 < datetime.strptime("2024.06.20", '%Y.%m.%d'):
            break

cursor.execute("select fund_code from fund_products_4")
codes = cursor.fetchall()

codes = [elem[0] for elem in codes]
# print(codes)

for code in codes:
    fund_price_crawl(code)

cursor.close()
# connection.close()
