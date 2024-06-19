
from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
import joblib

app = Flask(__name__)

mapping = {3: '매우공격적', 2: '공격적', 1: '안정적', 0: '소극적'}
map_func = np.vectorize(mapping.get)

@app.route('/predict', methods=['POST'])
def predict():
    global loaded_model
    try:
        data = request.json['data']
        print("입력 데이터:", data)
        
        # 모델 예측 (예시로서 model_layer 함수 사용)
        predictions = loaded_model.predict(data)  # model_layer 함수가 TensorFlow 텐서를 반환한다고 가정
        return_predict = map_func(predictions).tolist()
        print(return_predict)
        return jsonify({'predicted_class': return_predict })
        

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    global loaded_model
    model_path = 'loaded_model'
    loaded_model = joblib.load(model_path)
    print(f'Model loaded from {model_path}')

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)