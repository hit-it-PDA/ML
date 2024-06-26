import sys
import os
import pandas as pd
from pmdarima.arima import auto_arima
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from mysqlconnect import connect_to_mysql

connection = connect_to_mysql()

def get_arima_predict(code,kind):
    try :
        cursor = connection.cursor()
        prices = fetch_prices(cursor,code,kind)
        connection.commit()
        model = auto_arima(prices, start_p=1, start_q=1, 
                                    max_p=3, max_1=3, m=3, seasonal=False, # sarima(seasonal=True)
                                    d=1, D=0,
                                    max_P=3, max_Q=3, 
                                    # trace=True,
                                    error_action='ignore',
                                    suppress_warnings=True, 
                                    stepwise=False)
        pred = model.predict(n_periods=30).to_list()
        date_range = pd.date_range(start=prices.index[-1], periods=30, freq='D')
        future_data = pd.DataFrame(data=pred, index=date_range, columns=['Value'])
        
        result = {'예측값' : future_data.iloc[-1].item(), '예측일' : future_data.index[-1].strftime('%Y%m%d') ,"등락률" : round( (future_data.iloc[-1].item()/prices.iloc[-1].item() -1 )*100,2)}
        return result
        
    except Exception as e:
        return {"error" : "error"}
    
    
    
def fetch_prices(cursor, code, kind):
    # 현재 날짜 가져오기 => 2024-06-21 이런 느낌으로
    today = datetime.now() 
    today_str = today.strftime('%Y-%m-%d')
    
    data = []
    if kind == "fund" :
        query = f'select date, price from fund_prices where date between "2024-01-01" and "{today_str}" and fund_code = "{code}";'
    else :
        query = f'select date, price from stocks_products_details where date between "2024-01-01" and "{today_str}" and stock_code = "{code}";'
    
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        data.append(row)
    
    cursor.close()
    connection.close()  
    
    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df