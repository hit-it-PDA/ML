from flask import Flask, g
from utils.sql.sqlconnect import get_sql_connection

def create_app():
    print("__init__ in 'app' directory")
    app = Flask(__name__)
    
    
    
    # def get_db_connection():
    #     if 'connection' not in g:
    #         g.connection = get_sql_connection()
    #     return g.connection
    
    @app.before_request
    def before_request():
        g.connection = get_sql_connection()
        # g.cursor = g.connection.cursor()

    # @app.teardown_appcontext
    # def close_db_connection(exception):
    #     connection = g.pop('connection', None)
    #     if connection is not None:
    #         connection.close()

    from .ml.routes import ml
    from .mydata.routes import mydata

    app.register_blueprint(ml, url_prefix = "/ml")
    app.register_blueprint(mydata, url_prefix = "/mydata")
    
    return app