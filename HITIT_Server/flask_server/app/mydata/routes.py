from flask import Blueprint,jsonify,g,request
from datetime import datetime
from collections import defaultdict
import sys
import os
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from dart.routes import rev_income, rev_income2

mydata = Blueprint('mydata', __name__)

category_mapping = {1: '공격투자형', 2: '적극투자형', 3: '위험중립형', 4: '안정추구형', 5: '안정형'}

#펀드에 들어가있는 컬럼 다 저장(스프링서버에 다 넘겨줘야 되서)
fund_column_names = [
    'fund_code', 'fund_name', 'hashtag', 'std_price', 'set_date', 'fund_type',
    'fund_type_detail', 'set_amount', 'company_name', 'risk_grade', 'risk_grade_txt',
    'drv_nav', 'bond', 'bond_foreign', 'stock', 'stock_foreign', 'investment',
    'etc', 'return_1m', 'return_3m', 'return_6m', 'c', 'return_3y',
    'return_5y', 'return_idx', 'return_ytd', 'arima_price', 'arima_update',
    'arima_percent', "stock_ratio", "bond_ratio"
]

@mydata.route('/ttest',methods=['POST'])
def ttest():
    data = request.json
    stock_code = data['stock_code']
    rev, income = rev_income(stock_code)
    if rev == None and income == None : 
        rev, income = rev_income2(stock_code)
    return jsonify({"response" : {"rev" : rev, "income" : income}})

def funds_query_by_id(level, user_id, rand) : 
    #9개 열 기준
    order_list = ['return_1m','return_3m','return_6m','return_1y','return_3y','return_5y','return_idx','return_ytd','arima_percent']
    query = f"""
    WITH RankedProducts AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY company_name ORDER BY {order_list[user_id % 9]} DESC) AS rn
        FROM fund_products_4
        WHERE risk_grade >= {level} AND company_name <> '신한자산운용'
    ),
    TopShinhanProduct AS (
        SELECT *,
            1 AS rn
        FROM fund_products_4
        WHERE risk_grade >= {level} AND company_name = '신한자산운용'
        ORDER BY {order_list[user_id % 9]} DESC
        LIMIT 1
    )
    SELECT *
    FROM (
        SELECT *
        FROM RankedProducts
        WHERE rn = 1
        ORDER BY {order_list[user_id % 9]} DESC
        LIMIT 4
    ) AS TopRankedProducts

    UNION ALL

    SELECT *
    FROM TopShinhanProduct

    ORDER BY {order_list[user_id % 9]} DESC
    LIMIT 5;

    """
    return query

@mydata.route('/funds',methods=['POST'])
def getFunds():
    print("mydata/funds")
    data = request.json
    user_id = data['user_id']
    
    transactions, stockBalance, age,  wealth = data['transactions'], data['stockBalance'], data['age'],data['wealth']

    classmodel = g.classmodel
    connection = g.connection
    cursor = connection.cursor()
    # print(data)
    # print(transactions)
    avg_per = calculate_average_per(stockBalance,cursor)
    # avg_per = 12
    avg_trans_gap = calculate_average_holding_period(transactions)
    # avg_trans_gap = 20
    
    returned = classmodel.predict([[age,wealth,len(transactions),avg_per, avg_trans_gap]])
    print("returend", returned)
    user_class = returned.tolist()[0] + 1
    print("user_class : ", user_class)
    result_data = []
    if user_class <= 3: #유저가 1,2,3이라면
        for i in range(3) :
            result = fetchs_funds(user_class, user_id, i,cursor)
            result_data.append(result)
    elif user_class == 4:
        for i in range(2):
            result = fetchs_funds(user_class, user_id, i,cursor)
            result_data.append(result)
        for i in range(1):
            result = fetchs_funds(user_class, user_id, i, cursor)
            result_data.append(result)       
    else :
        for i in range(3):
            result = fetchs_funds(user_class, user_id, 0 , cursor)
            result_data.append(result)    
        
    return jsonify({"response" : result_data})


def get_two_bonds(user_id):
    # print(f"get two bonds {user_id}")
    order_list = ['return_1m','return_3m','return_6m','return_1y','return_3y','return_5y','return_idx','return_ytd','arima_percent']
    query =f"""\
    WITH company_funds AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY company_name ORDER BY {order_list[user_id % 9]} DESC) as row_num
    FROM fund_products_4
    WHERE risk_grade = 6 AND bond_ratio = 100 AND company_name <> '신한자산운용'
    )
    SELECT *
    FROM company_funds
    WHERE row_num = 1
    ORDER BY {order_list[user_id % 9]} DESC
    LIMIT 2;
    """
    return query

def funds_query_by_id_level(level, user_id, i) : 
    #9개 열 기준
    order_list = ['return_1m','return_3m','return_6m','return_1y','return_3y','return_5y','return_idx','return_ytd','arima_percent']
    query = f"""
    WITH RankedProducts AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY company_name ORDER BY {order_list[user_id % 9]} DESC) AS rn
        FROM fund_products_4
        WHERE risk_grade = {level + i} AND company_name <> '신한자산운용'
    ),
    TopShinhanProduct AS (
        SELECT *,
            1 AS rn
        FROM fund_products_4
        WHERE risk_grade = {level + i} AND company_name = '신한자산운용'
        ORDER BY {order_list[user_id % 9]} DESC
        LIMIT 1
    )
    
    
    SELECT *
    FROM (
        SELECT *
        FROM RankedProducts
        WHERE rn = 1
        ORDER BY {order_list[user_id % 9]} DESC
        LIMIT 2
    ) AS TopRankedProducts
    
    UNION ALL
    
    SELECT *
    FROM TopShinhanProduct
    ORDER BY {order_list[user_id % 9]} DESC
    
    LIMIT 5;

    """
    return query

def fetchs_funds(user_class, user_id, i, cursor):
    
    #주식말고 펀드 가져오기 쿼리
    query = funds_query_by_id_level(user_class, user_id, i)
    cursor.execute(query)
    fetched_data = cursor.fetchall()
    
    #채권 펀드 가져오기 쿼리
    query = get_two_bonds(user_id)
    cursor.execute(query)
    fetched_data2 = cursor.fetchall()
    # cursor.close()
    
    for elem in fetched_data2 :
        fetched_data.append(elem)
        
        
    data_dict = [dict(zip(fund_column_names, row)) for row in fetched_data]
    result = {"fund_class" : category_mapping[user_class+i],"funds" : data_dict}
    return result

def get_user_test_class(score):
    if score <= 8:
        return 5
    elif score <= 16 :
        return 4
    elif score <= 24 :
        return 3
    elif score <=32 :
        return 2
    else :
        return 1


@mydata.route('/fundss',methods=['POST'])
def getFund() :
    print("mydata/fundss")
    data = request.json
    user_id = data['user_id']
    user_level = data['level']
    
    classmodel, connection = g.classmodel, g.connection
    cursor = connection.cursor()
    
    user_class = user_level
    
    result_data = []
    if user_class <= 3: #유저가 1,2,3이라면
        for i in range(3) :
            result = fetchs_funds(user_class, user_id, i,cursor)
            result_data.append(result)
    elif user_class == 4:
        for i in range(2):
            result = fetchs_funds(user_class, user_id, i,cursor)
            result_data.append(result)
        for i in range(1):
            result = fetchs_funds(user_class, user_id, i, cursor)
            result_data.append(result)       
    else :
        for i in range(3):
            result = fetchs_funds(user_class, user_id, 0 , cursor)
            result_data.append(result)    
            
    # print(result_data)
    return jsonify({"response" : result_data})

@mydata.route('/funds/test',methods=['POST'])
def getFundsByTest():
    print("mydata/funds/test")
    data = request.json
    user_id = data['user_id']
    print(user_id)
    user_test_score = data['user_test_score']
    user_test_class = get_user_test_class(user_test_score)
    
    transactions, stockBalance, age,  wealth = data['transactions'], data['stockBalance'], data['age'],data['wealth']

    classmodel = g.classmodel
    connection = g.connection
    cursor = connection.cursor()
    
    avg_per = calculate_average_per(stockBalance,cursor)
    # avg_per = 12
    
    avg_trans_gap = calculate_average_holding_period(transactions)
    # avg_trans_gap = 20
    
    returned = classmodel.predict([[age,wealth,len(transactions),avg_per, avg_trans_gap]])
    
    user_class = returned.tolist()[0] + 1
    print(f"age : {age}, wealth : {wealth}, # of trans : {len(transactions)}, avg_per : {avg_per}, avg_trans_gap : {avg_trans_gap}")
    print(f"score : {user_test_score}, test_class : {user_test_class}, user_class :{user_class}")
    
    user_class = (user_class + user_test_class ) // 2

    result_data = []
    if user_class <= 3: #유저가 1,2,3이라면
        for i in range(3) :
            result = fetchs_funds(user_class, user_id, i,cursor)
            result_data.append(result)
    elif user_class == 4:
        for i in range(2):
            result = fetchs_funds(user_class, user_id, i,cursor)
            result_data.append(result)
        for i in range(1):
            result = fetchs_funds(user_class, user_id, i, cursor)
            result_data.append(result)       
    else :
        for i in range(3):
            result = fetchs_funds(user_class, user_id, 0 , cursor)
            result_data.append(result)    
        
    return jsonify({"response" : result_data})

#유저스타일 분류해주는 DB
@mydata.route('/style/<user_id>',methods=['GET'])
def style(user_id):
    print("style func",user_id)
    column_names = ['user_id','investment_style', 'investment_style_class','investment_test_class']
    
    connection = g.connection
    cursor = connection.cursor()
    
    cursor.execute(f"select user_id, investment_style, investment_style_class, investment_test_class  from user_style where user_id = {user_id}")
    fetched_data = cursor.fetchall()
    # cursor.close()
    # connection.close()
    
    data_dict = [dict(zip(column_names, row)) for row in fetched_data]
    print(data_dict)
    return jsonify({'result': data_dict[0]})

@mydata.route('/fundsrecom/<user_id>', methods = ['GET'])
def fund_mydata_recommendation(user_id):
    connection = g.connection
    cursor = connection.cursor()
    
    cursor.execute(f"select investment_style_class from user_style where user_id = {user_id}")
    row = cursor.fetchone()
    
    level = row[0]
    
    print(f"userid : {user_id}, risk : {level}")
    
    cursor.fetchall()
    
    query = get_funds_by_level(level)
    
    
    cursor.execute(query)
    fetched_data = cursor.fetchall()
    # cursor.close()
    # connection.close()
    
    data_dict = [dict(zip(fund_column_names, row)) for row in fetched_data]
    
    return jsonify({"result" : data_dict})
    

#유저의 등급에 따라 펀드 등급을 분류해준다
@mydata.route('/fundstest/<user_id>', methods = ['POST'])
def fund_test_recommendation(user_id):
    connection = g.connection
    cursor = connection.cursor()
    
    cursor.execute("select investment_test_class from user_style")
    row = cursor.fetchone()
    
    # cursor.close()
    # connection.close()
    query =f'''
    WITH RankedProducts AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY company_name ORDER BY arima_percent DESC) AS rn
        FROM fund_products_4
        WHERE risk_grade >= {risk}  AND company_name <> '신한자산운용'
    )
    SELECT *
    FROM (
        SELECT *
        FROM RankedProducts
        WHERE rn = 1

        UNION ALL

        SELECT * , 1 as rn
        FROM fund_products_4
        WHERE risk_grade >= {risk} AND company_name = '신한자산운용'
    ) AS CombinedResults
    ORDER BY arima_percent DESC
    LIMIT 5;
    '''
    cursor.execute(query)
    # cursor.close()
    # connection.close()
    
    fetched_data = cursor.fetchall()

    data_dict = [dict(zip(fund_column_names, row)) for row in fetched_data]
    return jsonify({"result" : data_dict})


def calculate_average_per(stocks, cursor):
    stock_pers = []
    print("sssssssssssssssssssssssssssssssssssss")
    for stock in stocks:
        print(stock)
        query = f"select per from stocks_products_details where stock_code = '{stock}' limit 1" 
        cursor.execute(query)
        row = cursor.fetchone()
        if row is not None :
            # row = [10]
            stock_pers.append(row[0])
    # print(stock_pers)
    if len(stock_pers) != 0:
        avg_per = round( sum(stock_pers)/len(stock_pers),2 )
    else :
        return 10
    # print(avg_per)

    if avg_per < 0 :
        return 0
    elif avg_per > 30 : 
        return 30
    else : 
        return avg_per

def calculate_average_holding_period(transactions):
    # 날짜 형식을 지정합니다.
    date_format = "%Y-%m-%d"

    # 주식 코드별로 매수와 매도 날짜를 저장할 딕셔너리입니다.
    holdings = defaultdict(list)

    for transaction in transactions:
        date_str = transaction['date']
        action = transaction['type']
        stock_code = transaction['code']
        # 날짜 형식이 올바른지 검증
        try:
            date = datetime.strptime(date_str, date_format)
        except ValueError:
            print(f"Invalid date format for transaction: {transaction}")
            continue
        holdings[stock_code].append((date, action))

    # 각 주식 코드에 대해 매수와 매도 날짜를 짝지어 기간을 계산합니다.
    total_days = 0
    total_transactions = 0

    for stock_code, actions in holdings.items():
        buy_dates = []
        sell_dates = []

        for date, action in actions:
            if action == 'buy':
                buy_dates.append(date)
            elif action == 'sell':
                sell_dates.append(date)

        # 매수 매도 쌍을 맞춥니다.
        while buy_dates and sell_dates:
            buy_date = buy_dates.pop(0)
            sell_date = sell_dates.pop(0)
            holding_period = (sell_date - buy_date).days
            total_days += holding_period
            total_transactions += 1

    # 평균 보유 기간을 계산합니다.
    if total_transactions == 0:
        return 0

    average_holding_period = total_days / total_transactions
    
    return average_holding_period