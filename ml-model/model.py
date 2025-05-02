import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from urllib.parse import urlparse
import re

class PhishingDetectionModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.max_sequence_length = 100
        self.vocab_size = 10000
        
    def build_model(self):
        """Build and compile the model with enhanced architecture"""
        # URL text input branch
        url_input = layers.Input(shape=(self.max_sequence_length,), name='url_input')
        
        # Reduce embedding dimensions
        embedding = layers.Embedding(
            self.vocab_size, 
            64,  # Reduced from 128
            input_length=self.max_sequence_length,
            embeddings_regularizer=tf.keras.regularizers.l2(1e-5)
        )(url_input)
        
        # Add dropout after embedding
        embedding = layers.Dropout(0.2)(embedding)
        
        # Simpler conv layers with L2 regularization
        conv1 = layers.Conv1D(64, 3, activation='relu', padding='same',
                            kernel_regularizer=tf.keras.regularizers.l2(1e-4))(embedding)
        conv2 = layers.Conv1D(64, 4, activation='relu', padding='same',
                            kernel_regularizer=tf.keras.regularizers.l2(1e-4))(embedding)
        
        # Max pooling
        pool1 = layers.GlobalMaxPooling1D()(conv1)
        pool2 = layers.GlobalMaxPooling1D()(conv2)
        
        # Concatenate pooled features
        concat = layers.Concatenate()([pool1, pool2])
        
        # Smaller dense layers with more dropout
        dense1 = layers.Dense(
            64,  # Reduced from 256
            activation='relu',
            kernel_regularizer=tf.keras.regularizers.l2(1e-4)
        )(concat)
        dropout1 = layers.Dropout(0.5)(dense1)
        
        # Output layer with regularization
        output = layers.Dense(
            1, 
            activation='sigmoid',
            kernel_regularizer=tf.keras.regularizers.l2(1e-4)
        )(dropout1)
        
        # Create model
        model = models.Model(inputs=url_input, outputs=output)
        
        # Compile with enhanced metrics
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),  # Reduced learning rate
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall'),
                tf.keras.metrics.AUC(name='auc')
            ]
        )
        
        self.model = model
        return model
    
    def prepare_tokenizer(self, texts):
        """Create and fit tokenizer on training data"""
        tokenizer = tf.keras.preprocessing.text.Tokenizer(
            num_words=self.vocab_size,
            filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n',
            lower=True,
            split=' ',
            char_level=False
        )
        tokenizer.fit_on_texts(texts)
        self.tokenizer = tokenizer
        return tokenizer
    
    def preprocess_text(self, texts):
        """Convert texts to sequences and pad them"""
        if self.tokenizer is None:
            raise ValueError("Tokenizer not initialized. Call prepare_tokenizer first.")
            
        sequences = self.tokenizer.texts_to_sequences(texts)
        padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(
            sequences, maxlen=self.max_sequence_length, padding='post', truncating='post'
        )
        return padded_sequences
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """Train the model with early stopping and learning rate reduction"""
        if self.model is None:
            self.build_model()
            
        # Add callbacks for better training
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=0.00001
            )
        ]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
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

def extract_url_features(url):
    """Extract enhanced features from URL for ML model"""
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
    features['has_http'] = int(url.startswith('http://'))
    
    # Domain features
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query
        
        # Domain analysis
        features['domain_length'] = len(domain)
        features['subdomain_count'] = domain.count('.')
        features['is_ip'] = int(all(c.isdigit() or c == '.' for c in domain))
        features['has_suspicious_tld'] = int(domain.endswith(('.xyz', '.info', '.online', '.site', '.biz')))
        
        # Path analysis
        features['path_length'] = len(path)
        features['path_depth'] = path.count('/')
        features['has_suspicious_path'] = int(any(word in path.lower() for word in ['login', 'signin', 'account', 'verify', 'secure', 'update']))
        
        # Query analysis
        features['query_length'] = len(query)
        features['num_params'] = query.count('&') + 1 if query else 0
        
        # Additional security indicators
        features['has_port'] = int(':' in domain)
        features['port_number'] = int(domain.split(':')[1]) if ':' in domain else 0
        features['has_credentials'] = int('@' in url)
        
    except:
        # Default values if parsing fails
        features.update({
            'domain_length': 0,
            'subdomain_count': 0,
            'is_ip': 0,
            'has_suspicious_tld': 0,
            'path_length': 0,
            'path_depth': 0,
            'has_suspicious_path': 0,
            'query_length': 0,
            'num_params': 0,
            'has_port': 0,
            'port_number': 0,
            'has_credentials': 0
        })
    
    return features 