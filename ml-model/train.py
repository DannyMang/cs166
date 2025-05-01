import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from model import PhishingDetectionModel, extract_url_features
import os

def load_data(phishing_csv, legitimate_csv):
    """Load and prepare the dataset"""
    # Load phishing URLs
    phishing_df = pd.read_csv(phishing_csv)
    phishing_df['label'] = 1  # 1 for phishing
    
    # Load legitimate URLs
    legitimate_df = pd.read_csv(legitimate_csv)
    legitimate_df['label'] = 0  # 0 for legitimate
    
    # Combine datasets
    combined_df = pd.concat([phishing_df, legitimate_df], ignore_index=True)
    
    # Shuffle the data
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)
    
    return combined_df

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # For demonstration, we'll create sample data
    # In a real project, you would use actual phishing and legitimate URLs
    print("Creating sample data...")
    
    # Sample phishing URLs
    phishing_urls = [
        'http://paypal-secure.com/login',
        'http://amazon-account-verify.com',
        'http://secure-banking-login.com',
        'http://facebook-verify.com/login',
        'http://apple-id-confirm.com',
        # Add more examples...
    ]
    
    # Sample legitimate URLs
    legitimate_urls = [
        'https://www.paypal.com/login',
        'https://www.amazon.com',
        'https://www.bankofamerica.com',
        'https://www.facebook.com',
        'https://www.apple.com',
        # Add more examples...
    ]
    
    # Create sample dataframes
    phishing_df = pd.DataFrame({'url': phishing_urls})
    legitimate_df = pd.DataFrame({'url': legitimate_urls})
    
    # Save to CSV
    phishing_df.to_csv('data/phishing_urls.csv', index=False)
    legitimate_df.to_csv('data/legitimate_urls.csv', index=False)
    
    # Load data
    print("Loading data...")
    data = load_data('data/phishing_urls.csv', 'data/legitimate_urls.csv')
    
    # Create model instance
    model = PhishingDetectionModel()
    
    # Prepare tokenizer
    print("Preparing tokenizer...")
    model.prepare_tokenizer(data['url'])
    
    # Extract features and preprocess URLs
    print("Processing URLs...")
    X = model.preprocess_text(data['url'])
    y = data['label'].values
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    # Train model
    print("Training model...")
    model.train(X_train, y_train, X_val, y_val, epochs=20, batch_size=32)
    
    # Evaluate model
    print("Evaluating model...")
    loss, accuracy, precision, recall = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {accuracy:.4f}")
    print(f"Test precision: {precision:.4f}")
    print(f"Test recall: {recall:.4f}")
    
    # Save model and tokenizer
    print("Saving model and tokenizer...")
    model.save('data/url_model.h5', 'data/tokenizer.pkl')
    
    print("Done!")

if __name__ == "__main__":
    main() 