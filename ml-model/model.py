import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

class PhishingDetectionModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.max_sequence_length = 100
        self.vocab_size = 10000
        
    def build_model(self):
        """Build and compile the model"""
        model = models.Sequential([
            layers.Embedding(self.vocab_size, 64, input_length=self.max_sequence_length),
            layers.Conv1D(128, 5, activation='relu'),
            layers.GlobalMaxPooling1D(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
        
        self.model = model
        return model
    
    def prepare_tokenizer(self, texts):
        """Create and fit tokenizer on training data"""
        tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self.vocab_size)
        tokenizer.fit_on_texts(texts)
        self.tokenizer = tokenizer
        return tokenizer
    
    def preprocess_text(self, texts):
        """Convert texts to sequences and pad them"""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not initialized. Call prepare_tokenizer first.")
            
        sequences = self.tokenizer.texts_to_sequences(texts)
        padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(
            sequences, maxlen=self.max_sequence_length, padding='post'
        )
        return padded_sequences
    
    def train(self, X_train, y_train, X_val, y_val, epochs=10, batch_size=32):
        """Train the model"""
        if self.model is None:
            self.build_model()
            
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        if self.model is None:
            raise ValueError("Model not trained. Call train first.")
            
        return self.model.evaluate(X_test, y_test)
    
    def predict(self, texts):
        """Predict if texts are phishing attempts"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model or tokenizer not initialized.")
            
        processed_texts = self.preprocess_text(texts)
        predictions = self.model.predict(processed_texts)
        return predictions
    
    def save(self, model_path, tokenizer_path):
        """Save the model and tokenizer"""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model or tokenizer not initialized.")
            
        self.model.save(model_path)
        
        import pickle
        with open(tokenizer_path, 'wb') as f:
            pickle.dump(self.tokenizer, f)
    
    @classmethod
    def load(cls, model_path, tokenizer_path):
        """Load a saved model and tokenizer"""
        instance = cls()
        
        instance.model = models.load_model(model_path)
        
        import pickle
        with open(tokenizer_path, 'rb') as f:
            instance.tokenizer = pickle.load(f)
            
        return instance

# URL feature extraction functions
def extract_url_features(url):
    """Extract features from URL for ML model"""
    features = {}
    
    # Basic URL properties
    features['length'] = len(url)
    features['num_dots'] = url.count('.')
    features['num_hyphens'] = url.count('-')
    features['num_underscores'] = url.count('_')
    features['num_slashes'] = url.count('/')
    features['num_question_marks'] = url.count('?')
    features['num_equal_signs'] = url.count('=')
    features['num_at_symbols'] = url.count('@')
    features['num_ampersands'] = url.count('&')
    features['num_digits'] = sum(c.isdigit() for c in url)
    
    # Protocol features
    features['has_https'] = int(url.startswith('https://'))
    
    # Domain features
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        features['domain_length'] = len(domain)
        features['subdomain_count'] = domain.count('.') 
        features['is_ip'] = int(all(c.isdigit() or c == '.' for c in domain))
        
    except:
        features['domain_length'] = 0
        features['subdomain_count'] = 0
        features['is_ip'] = 0
    
    return features 