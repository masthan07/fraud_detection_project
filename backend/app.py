from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import pickle
import os
from datetime import datetime
from model_handler import FraudDetectionModel

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app, origins=['*'])  # Allow access from anywhere

# Load model on startup
MODEL_PATH = os.path.join('models', 'xgb_fraud_detector.pkl')

try:
    with open(MODEL_PATH, 'rb') as f:
        xgb_model = pickle.load(f)
    fraud_detector = FraudDetectionModel(xgb_model)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    fraud_detector = None

@app.route('/')
def home():
    return send_file('../frontend/index.html')

@app.route('/api')
def api_status():
    return jsonify({
        'status': 'running',
        'message': 'Fraud Detection API',
        'model_loaded': fraud_detector is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    if fraud_detector is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Get input data
        data = request.json
        
        # Validate required fields
        required_fields = ['amount', 'cardType', 'cardLast4', 'deviceType', 
                          'country', 'zipCode', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Make prediction
        result = fraud_detector.predict(data)
        
        # Add metadata
        result['transaction_id'] = f"TXN{int(datetime.now().timestamp())}"
        result['timestamp'] = datetime.now().isoformat()
        result['amount'] = float(data['amount'])
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)