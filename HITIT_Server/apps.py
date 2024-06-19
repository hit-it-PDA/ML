from transformers import pipeline
from flask import Flask, request, jsonify
import numpy as np
import joblib

# 감정 분석 파이프라인 로드
mapping = {3: '매우공격적', 2: '공격적', 1: '안정적', 0: '소극적'}
map_func = np.vectorize(mapping.get)

app = Flask(__name__)

def get_sentiment(text):
    result = sentiment_model(text)
    for elem in result:
        if elem['label'] == "LABEL_1":
            elem['label'] = "POSITIVE"
        else:
            elem['label'] = "NEGATIVE"
        elem['score'] = round(elem['score'], 5)

    print(f"Sentiment analysis result: {result}")
    return result

@app.route('/predict', methods=['POST'])
def predict():
    global loaded_model
    try:
        data = request.json['data']
        print("입력 데이터:", data)
        
        # 모델 예측
        predictions = loaded_model.predict(data)  # model_layer 함수가 TensorFlow 텐서를 반환한다고 가정
        return_predict = map_func(predictions).tolist()
        print(return_predict)
        return jsonify({'predicted_class': return_predict})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/sentiment', methods=['POST'])
def sentiment():
    global sentiment_model
    try:
        data = request.json['data']
        sentiment_result = get_sentiment(data)
        return jsonify({'sentiment_analysis': sentiment_result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    global sentiment_model
    sentiment_model = pipeline(model="WhitePeak/bert-base-cased-Korean-sentiment")
    
    global loaded_model
    model_path = './RF/loaded_model'
    loaded_model = joblib.load(model_path)
    print(f'Model loaded from {model_path}')

    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    