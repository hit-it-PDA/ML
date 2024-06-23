from transformers import pipeline
from flask import Flask, request, jsonify, g
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

from app import create_app

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)