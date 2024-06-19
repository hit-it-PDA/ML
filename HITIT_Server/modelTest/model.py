import boto3
import tarfile
import os
import tensorflow as tf
import numpy as np
from keras.layers import TFSMLayer

# # 추출된 모델 디렉토리 경로 설정 (saved_model.pb 파일의 경로)
saved_model_dir = 'model'
model_save_path = 'tf_model'

try:
    model_layer = TFSMLayer(saved_model_dir, call_endpoint="serving_default")
    print(f'Model loaded from {saved_model_dir}')
except Exception as e:
    print(f"Error loading model with TFSMLayer: {e}")

# 예시 입력 데이터 (모델에 맞게 수정 필요)
input_data = np.random.rand(1, 28, 28).astype(np.float32)
input_tensor = tf.constant(np.expand_dims(input_data, axis=-1))  # 차원 추가: (1, 28, 28, 1)

# 모델 예측
try:
    predictions = model_layer(input_tensor)
    # print(f'Predictions: {predictions}')
    print(predictions['dense_1'].numpy())
except Exception as e:
    print(f"Error making predictions: {e}")
