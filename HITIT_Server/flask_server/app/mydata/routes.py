from flask import Blueprint,jsonify,g

mydata = Blueprint('mydata', __name__)

fund_column_names = [
    'fund_code', 'fund_name', 'hashtag', 'std_price', 'set_date', 'fund_type',
    'fund_type_detail', 'set_amount', 'company_name', 'risk_grade', 'risk_grade_txt',
    'drv_nav', 'bond', 'bond_foreign', 'stock', 'stock_foreign', 'investment',
    'etc', 'return_1m', 'return_3m', 'return_6m', 'return_1y', 'return_3y',
    'return_5y', 'return_idx', 'return_ytd', 'arima_price', 'arima_update',
    'arima_percent'
]

@mydata.route('/',methods=['POST'])
def main():
    return jsonify({'result': "hi"})


@mydata.route('/style/<user_id>',methods=['GET'])
def style(user_id):
    print("style func",user_id)
    column_names = ['user_id','investment_style', 'investment_style_class','investment_test_class']
    
    connection = g.connection
    cursor = connection.cursor()
    
    cursor.execute(f"select user_id, investment_style, investment_style_class, investment_test_class  from user_style where user_id = {user_id}")
    fetched_data = cursor.fetchall()
    
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
    
    query = \
    f"""WITH RankedProducts AS (
        SELECT *,
        ROW_NUMBER() OVER (PARTITION BY company_name ORDER BY arima_percent DESC) AS rn
        FROM fund_products_4
        WHERE risk_grade >= {level} AND company_name <> '신한자산운용'
    )
    SELECT *
    FROM (
        SELECT *
        FROM RankedProducts
        WHERE rn = 1

        UNION ALL

        SELECT * , 1 as rn
        FROM fund_products_4
        WHERE risk_grade >= {level} AND company_name = '신한자산운용'
    ) AS CombinedResults
    ORDER BY arima_percent DESC
    LIMIT 5;
    """
    
    
    cursor.execute(query)
    fetched_data = cursor.fetchall()
    data_dict = [dict(zip(fund_column_names, row)) for row in fetched_data]
    
    return jsonify({"result" : data_dict})
    
    
@mydata.route('/fundstest/<user_id>', methods = ['POST'])
def fund_test_recommendation(user_id):
    connection = g.connection
    cursor = connection.cursor()
    
    cursor.execute("select investment_test_class from user_style")
    row = cursor.fetchone()
    
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
    fetched_data = cursor.fetchall()

    data_dict = [dict(zip(fund_column_names, row)) for row in fetched_data]
    return jsonify({"result" : data_dict})