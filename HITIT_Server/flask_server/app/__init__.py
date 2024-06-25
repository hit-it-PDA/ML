from flask import Flask, g
from utils.sql.sqlconnect import get_sql_connection
import joblib
import os

classmodel = None
connection = None


def create_app():
    print("__init__ in 'app' directory")
    app = Flask(__name__)
    
    # 애플리케이션 초기화 시 한 번만 모델 로드
    global classmodel
    global connection

    # 애플리케이션 초기화 시 한 번만 SQL 연결 설정
    if connection is None:
        connection = get_sql_connection()
        print("SQL connection established")

    if classmodel is None:
        # model_path = '/home/ubuntu/code/DE_ML/HITIT_Server/RF/loaded_model'
        model_path = '/home/ubuntu/code/DE_ML/HITIT_Server/My_data/loaded_model_0623.joblib'
        classmodel = joblib.load(model_path)
        print("model_loaded")

    @app.before_request
    def before_request():
        g.classmodel = classmodel
        g.connection = connection

    from .ml.routes import ml
    from .mydata.routes import mydata
    from .rebal.routes import rebal
    from .dart.routes import dart


    # cache = setup_cache(app)
    
    app.register_blueprint(ml, url_prefix = "/ml")
    app.register_blueprint(mydata, url_prefix = "/mydata")
    app.register_blueprint(rebal, url_prefix = "/rebal")
    app.register_blueprint(dart, url_prefix = "/dart")
    
    
    return app