import requests
import sys
import requests
from datetime import datetime, timedelta
import requests
import sys
import os
import pandas as pd
from bs4 import BeautifulSoup

def get_sentiment(sentiment_model,text):
    result = sentiment_model(text)
    for elem in result :
        if elem['label'] == "LABEL_1" :
            elem['label'] = "POSITIVE"
        else :
            elem['label'] = "NEGATIVE"
        elem['score'] = round(elem['score'],5)
    
    # print(f"Sentiment analysis result: {result}")
    return result[0]

def naver_news_crawling(keyword_list, sday,eday):
    result_object = {}  # 결과를 저장할 객체

    for keyword in keyword_list:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={sday}&de={eday}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom20240101to20240101&is_sug_officeid=0&office_category=0&service_area=0"
        
        response = requests.get(url,headers={'Content-Type': 'application/json'})
        soup = BeautifulSoup(response.content, 'html.parser')
        result = []
        # print(soup)
        for item in soup.select('.news_wrap'):
            press_element = item.select_one('a.info.press')
            # print()
            press = item.select_one('a.info.press').get_text().replace(' 선정', '').strip()
            anchor = item.select_one('a.news_tit')
            title = anchor.get_text().strip()
            url = anchor['href']
            dsc = item.select_one('.news_dsc').get_text().strip()

            result.append({
                'press': press,
                'title': title,
                'url': url,
                'dsc': dsc,
            })

        result_object[keyword] = result  # 키워드를 키로 사용하여 결과 저장
    return result_object  # 객체 반환
