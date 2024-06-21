import os
import sys
sys.path.append("/home/ubuntu/code/DE_ML/HITIT_Server")

from mysqlconnect import connect_to_mysql

connection = connect_to_mysql()

def get_sql_connection():
    return connection