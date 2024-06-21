import os
import asyncio
import pandas as pd
import pandas_datareader.data as pdr

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib

import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima.arima import auto_arima

import itertools
import pmdarima as pm
import time
import sys
import time

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta

# 현재 날짜 가져오기
today = datetime.now() 

# 날짜를 YYYYMMDD 형식으로 변환
today_str = today.strftime('%Y%m%d')
one_year_ago = today - timedelta(days=365)
one_year_ago_str = one_year_ago.strftime('%Y%m%d')
print(today_str,one_year_ago_str)