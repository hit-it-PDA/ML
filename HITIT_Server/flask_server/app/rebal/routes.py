import joblib
from flask import Blueprint,jsonify,g,request


import sys
import os
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from dart.routes import rev_income, rev_income2

rebal = Blueprint('rebal', __name__)

def normalize_weights(weights, ignore_indices=None):
    print()
    print()
    print("in function~")
    print(weights)
    if ignore_indices is None:
        total_sum = sum(weights)
        normalized_weights = [round(w / total_sum, 3) for w in weights]
        print("normalize")
        print(normalized_weights)
    else:
        # 무시할 인덱스를 고려한 정규화 수행
        print(weights, ignore_indices)
        total_sum = sum(w for i, w in enumerate(weights) if i not in ignore_indices)
        target_total = 1 - sum(weights[i] for i in ignore_indices)
        normalized_weights = []
        for i, weight in enumerate(weights):
            if i in ignore_indices:
                normalized_weights.append(weight)
            else:
                normalized_weight = (weight / total_sum) * target_total
                normalized_weights.append(round(normalized_weight, 3))
        print(normalized_weights)
    return normalized_weights

def get_sentiment_stock(code):
    return f"""
    SELECT
        fs.fund_code,
        fs.stock_name,
        sp.stock_code,
        sp.name AS stock_name,
        sp.sentiment,
        sp.bad_news_title as bad_news_title,
        sp.bad_news_url as bad_news_url
    FROM
        fund_stocks fs
    JOIN
        stocks_products sp ON fs.stock_name = sp.name
    WHERE   
        fs.fund_code = '{code}';
    """
    
@rebal.route('/getweight',methods=['POST'])
def getUserClass():
    print("rebel/getweight")
    data = request.json
    print(data)
    fund_codes = []
    weights = []
    user_id = data['user_id']
    num_of_stock_funds = data['stock_fund_count']
    overseas_indexs= data['overseas_indexes']
    for elem in data['funds']:
        code ,weight = elem['fund_code'], elem['weight']
        fund_codes.append(code)
        weights.append(weight)

    connection = g.connection
    cursor = connection.cursor()
    # 펀드 1개당 종목 : sentiment 담기
    sentiment_infos = []
    count_positive = []
    print("wegihtss", weights)
    for i in range(num_of_stock_funds):
        fund_code = fund_codes[i]
        # print(f"----------------{fund_code}-----------------")
        query = get_sentiment_stock(fund_code)
        cursor.execute(query)
        rows = cursor.fetchall()
        
        sentiment_info = []
        
        positive = 0
        print(f"fund_code : {fund_code}")
        for elem in rows:
            code, name, sentiment, stock_code,bad_news_title, bad_news_url = elem[0], elem[1], elem[4], elem[2], elem[5], elem[6]
            print((name,sentiment,bad_news_title))
            #
            if sentiment == 0:
                sentiment_info.append((code, name,sentiment,stock_code,bad_news_title,bad_news_url))
            elif sentiment == 1:
                positive += 1
        print("감정 : ",positive)
        count_positive.append(positive)
        sentiment_infos.append(sentiment_info)
                
            #
            # if sentiment == 1:
            #     sentiment_info.append((code, name,sentiment,stock_code))
            
    for funds in sentiment_infos:
        fund_idx = sentiment_infos.index(funds)
        print("fund idx" , fund_idx)
        print(f"fund_idx : {fund_idx}")
        # if len(funds) <= 3 :
        if count_positive[fund_idx] <= 3 :
            # if fund_idx not in overseas_indexs :
                # print("normalize")
            if overseas_indexs and fund_idx not in overseas_indexs:
                # weights = [ weight+0.01 for weight in weights ]
                # print(weight[])
                temp = 0
                for i in range((num_of_stock_funds)):
                    if i not in overseas_indexs :
                        temp += 1
                        
                weights[fund_idx] -= 0.01 * temp
                
                for i in range(num_of_stock_funds):
                    if i not in overseas_indexs:
                        weights[i] += 0.01
                print(weights)
                normalize_weights(weights, overseas_indexs)
            else :
                #     weights = normalize_weights(weights,overseas_indexs)
                # else :
                temp = 0
                for i in range((num_of_stock_funds)):
                    if i not in overseas_indexs and count_positive[i] <= 3:
                    # if i not in overseas_indexs:
                        temp += 1
                print("temp : ",temp)
                weights[fund_idx] -= 0.01 * temp
                
                for i in range(num_of_stock_funds):
                    if i not in overseas_indexs and count_positive[i] <= 3:
                    # if i not in overseas_indexs:
                        weights[i] += 0.01
                print("weighttttttttttttt", weights)
                # weights = [ weight + 0.01 for weight in weights]
                # weights[fund_idx] -= 0.05
                # print(weights)
                weights = normalize_weights(weights,overseas_indexs)
                print(weights)
            # print(weights)
        else :
            # sentiment_infos.remove(funds)
            sentiment_infos[fund_idx] = None
            
    results = {}
    results_temp = []
    
    print(count_positive)
    print(sentiment_infos)
    
    for elem in sentiment_infos:
        result = []
        if elem : 
            fund_code = elem[0][0]
        else :
            continue
        for stock in elem :
            title,url = stock[4], stock[5]
            title = "None" if title is None else stock[4]
            url = "None" if url is None else stock[5]
            
            rev, income = rev_income(stock[3])
            if rev == None and income == None : 
                rev, income = rev_income2(stock[3])
            
            result.append({"stock_code" : stock[3],"stock_name" : stock[1],"bad_news_title" : title ,"bad_news_url": url,"rev":str(rev), "income" : str(income)})
        results_temp.append({"fund_code" : fund_code, "stocks" : result})
    results['funds'] = results_temp
    results['weights'] = weights
    results['user_id'] = user_id
    
    return jsonify({"response" : results})