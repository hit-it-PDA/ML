import joblib
import os
from flask import Blueprint,jsonify,g,request
from dotenv import load_dotenv
import dart_fss as DART
import pandas as pd
import OpenDartReader
import requests
import sys

load_dotenv()

dart = Blueprint('dart', __name__)
dart_key = os.getenv('dart_key')

# DART부르기 위한 객체 생성
DART.set_api_key(api_key=dart_key)
DART = OpenDartReader(dart_key)

@dart.route('/info',methods=['POST'])
def get_rev_income(): 
    print('dart/info')   
    data = request.json
    stock_name = data['stock_name']
    
    connection = g.connection
    cursor = connection.cursor()
    
    #종목이름을 코드로 변환하기 위해 종목 코드 찾기
    cursor.execute(f"select stock_code from stocks_products where name='{stock_name}'")
    row = cursor.fetchone()
    if row :
        stock_code = row[0]
    else :
        return jsonify({"response" : None})
    
    print(f"converted to {stock_code}")
    rev, income = rev_income(stock_code)
    
    if rev == None and income == None : 
        rev, income = rev_income2(stock_code)
    return jsonify({"response" : {"rev" : rev, "income" : income}})

# 종목 코드를 배열로 받기
@dart.route('/infos',methods=['POST'])
def get_rev_incomes():
    print("/dart/info")
    data = request.json
    
    infos = []
    stock_codes = data['stock_codes'] #  배열
    for code in stock_codes: # code는 딕셔너리 하나
        stock_code = code['stock_code'] # 딕셔너리 안에 종목 코드 가져오기
        temp_info = {}
        rev, income = rev_income(stock_code)
        if rev == None and income == None : 
            rev, income = rev_income2(stock_code)
        temp_info['code'] = {"rev" : rev, "income" : income}
        infos.append(temp_info)
        
    return jsonify({"response" : {"infos" : infos}})

def rev_income(code):
    print("call_rev_income")
    try : 
        returned = DART.finstate(corp=code, bsns_year=2023).iloc[9:11]
        매출 = returned.iloc[0,]['thstrm_amount']
        영업이익 = returned.iloc[1,]['thstrm_amount']
        매출 = int(매출.replace(",", ""))
        영업이익 = int(영업이익.replace(",", ""))
        return 매출, 영업이익
    except : 
        return None, None
    

def rev_income2(code):
    print("call_rev_income2")
    url = f'https://m.stock.naver.com/api/stock/{code}/finance/annual'
    # url = f'https://m.stock.naver.com/api/stock/133820/finance/annual'
    try : 
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        data = response.json()['financeInfo']['rowList']
        
        매출 = data[0]['columns']['202312']['value'] 
        매출 = int(매출.replace(",", "")) * 100000000
        영업이익 = data[1]['columns']['202312']['value']
        영업이익 = int(영업이익.replace(",", ""))* 100000000
        
        return 매출, 영업이익
    except :    
        print("can't find rev")
        return None, None