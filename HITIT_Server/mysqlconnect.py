import mysql.connector
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 불러오기
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

def connect_to_mysql():
    print(f"USER: {USER}, HOST: {HOST}, PORT: {PORT}, DATABASE: {DATABASE}")
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=int(PORT),
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
    return connection
