import joblib
from flask import Blueprint,jsonify,g,request


rebal = Blueprint('rebal', __name__)

def normalize_weights(weights):
    print("weigths adjust")
    total_sum = sum(weights)
    normalized_weights = [round(w / total_sum , 3) for w in weights]
    return normalized_weights

def get_sentiemtn_stock(code):
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
    for elem in data['funds']:
        code ,weight = elem['fund_code'], elem['weight']
        fund_codes.append(code)
        weights.append(weight)

    connection = g.connection
    cursor = connection.cursor()
    # 펀드 1개당 종목 : sentiment 담기
    sentiment_infos = []
    count_positive = []
    for i in range(3):
        fund_code = fund_codes[i]
        print(f"----------------{fund_code}-----------------")
        query = get_sentiemtn_stock(fund_code)
        cursor.execute(query)
        rows = cursor.fetchall()
        sentiment_info = []
        
        positive = 0
        
        for elem in rows:
            code, name, sentiment, stock_code,bad_news_title, bad_news_url = elem[0], elem[1], elem[4], elem[2], elem[5], elem[6]
            print((code, name,sentiment,stock_code,bad_news_title,bad_news_url))
            #
            if sentiment == 0:
                sentiment_info.append((code, name,sentiment,stock_code,bad_news_title,bad_news_url))
            elif sentiment == 1:
                positive += 1
                
        count_positive.append(positive)
                
            #
            # if sentiment == 1:
            #     sentiment_info.append((code, name,sentiment,stock_code))
            
        sentiment_infos.append(sentiment_info)
    
    print(count_positive)
    for funds in sentiment_infos:
        fund_idx = sentiment_infos.index(funds)
        # if len(funds) <= 3 :
        if count_positive[fund_idx] <= 3 :
            weights = [ weight + 0.01 for weight in weights]
            weights[fund_idx] -= 0.05
            weights = normalize_weights(weights)
            # print(weights)
        # else :
            sentiment_infos.remove(funds)
            
    results = {}
    results_temp = []
    # print(sentiment_infos)
    print(positive)
    for elem in sentiment_infos:
        result = []
        fund_code = elem[0][0]
        for stock in elem :
            title,url = stock[4], stock[5]
            title = "None" if title is None else stock[4]
            url = "None" if url is None else stock[5]
            result.append({"stock_code" : stock[3],"stock_name" : stock[1],"bad_news_title" : title ,"bad_news_url": url})
        results_temp.append({"fund_code" : fund_code, "stocks" : result})
    results['funds'] = results_temp
    results['weights'] = weights
    results['user_id'] = user_id
    
    return jsonify({"response" : results})