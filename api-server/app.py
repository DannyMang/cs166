from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the ml-model directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml-model'))

from model import PhishingDetectionModel

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

# Global model instance
model = None

def load_model():
    """Load the trained model"""
    global model
    try:
        model = PhishingDetectionModel.load(
            model_path='../ml-model/data/url_model.h5',
            tokenizer_path='../ml-model/data/tokenizer.pkl'
        )
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to predict if a URL is phishing"""
    if model is None:
        return jsonify({
            'error': 'Model not loaded',
            'success': False
        }), 503

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'error': 'No URL provided',
            'success': False
        }), 400

    url = data['url']
    try:
        # Make prediction
        prediction = model.predict([url])[0][0]
        
        return jsonify({
            'success': True,
            'url': url,
            'is_phishing': bool(prediction > 0.5),
            'confidence': float(prediction)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True) 