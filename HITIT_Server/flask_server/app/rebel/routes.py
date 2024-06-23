from flask import Blueprint
import joblib


rebel = Blueprint('', __name__)

@ml.route('/class',methods=['POST'])
def getUserClass():
    
    # print(transactions, stockBalance,age,wealth)
    return jsonify({"response" : "good"})