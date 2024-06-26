import sys
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import sys
import os
import time
import pandas as pd
import re
from transformers import pipeline
from bs4 import BeautifulSoup
# 감정 분석 파이프라인 로드
sentiment_model = pipeline(model="WhitePeak/bert-base-cased-Korean-sentiment")

project_root = '/home/ubuntu/code/DE_ML/HITIT_Server'


sys.path.append(project_root)

from flask_server.utils.sql.sqlconnect import get_sql_connection

from sentiment_func import get_sentiment, naver_news_crawling

connection = get_sql_connection()
cursor = connection.cursor()

def insert_bad_news(code, title, url) :    
    cleaned_title = re.sub(r"[\"']", "", title)
    
    query = f"""
    UPDATE stocks_products
    SET bad_news_title = '{cleaned_title}',
        bad_news_url = '{url}'
    WHERE stock_code = '{code}';
    """
    # print(query)
    cursor.execute(query)
    cursor.close()
    connection.commit()
    print(f"insert 성공 , {code}")
    return

# query = "select stock_code,name from stocks_products where (DATE(sentiment_update) IS NULL OR DATE(sentiment_update) <> DATE(NOW()))"
query = "select stock_code,name from stocks_products where bad_news_title is null"
cursor.execute(query)
rows = cursor.fetchall()
print(len(rows))
stocks = [ elem[:2] for elem in rows] #(종목코드, 종목명 가져와보리기) DB에서
cursor.close()
# connection.close()

current_date = datetime.now().strftime("%Y.%m.%d")

current_date = datetime.strptime(current_date, "%Y.%m.%d")
current_date_before_oneMonth = current_date - timedelta(days=30)
current_date_before_oneMonth = current_date_before_oneMonth.strftime("%Y.%m.%d")
# current_date_before_oneMonth_str = current_date_before_oneMonth.strftime("%Y.%m.%d")

# 감정 분석 파이프라인 로드
from transformers import pipeline
sentiment_model = pipeline(model="WhitePeak/bert-base-cased-Korean-sentiment")

# results = naver_news_crawling(["삼성전자"], current_date, current_date)
# print(results)
        
for elem in stocks:
    time.sleep(2)
    try : 
        results = naver_news_crawling([elem[1]],current_date, current_date)

        if len(results[elem[1]]) == 0:
            results = naver_news_crawling([elem[1]], current_date_before_oneMonth, current_date)
        # print(results)

        print(f"index : {stocks.index(elem)}/{len(stocks)}, {elem[1]}")
        bad_news_insert = False

        for keyword, articles in results.items():
            positive, negative = 0, 0
            for article in articles: 
                title = article['title'].replace("'", "").replace('"', "").replace(".","")
                returned = get_sentiment(sentiment_model, title)
                # The `print(returned)` statement is printing the output of the `get_sentiment`
                # function for each article title. The `get_sentiment` function likely analyzes the
                # sentiment of the given text (in this case, the article title) using a sentiment
                # analysis model and returns a dictionary containing information about the sentiment
                # analysis result, such as the sentiment label (e.g., "POSITIVE" or "NEGATIVE").
                # print(returned)
                if returned['label'] == "NEGATIVE":
                    positive += 1
                    if  bad_news_insert == False :
                        insert_bad_news(elem[0],article['title'],article['url'])
                        bad_news_insert = True
                else :
                    negative += 1
            sentiment = 1 if positive > negative else 0
            
            # print(query)
            query = f"""\
            UPDATE stocks_products 
            SET sentiment = {sentiment},
            sentiment_update = NOW()
            where stock_code = {elem[0]}
            """
            cursor.execute(query)
            connection.commit()
            print(f"update 성공 ,{sentiment}")
    except:
        print(f"PASS {keyword}")
        continue
        
# connection.close()