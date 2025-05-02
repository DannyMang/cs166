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

def generate_phishing_urls(n=1000):
    """Generate synthetic phishing URLs with varying levels of suspiciousness"""
    legitimate_domains = ['paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook', 'netflix', 'bank', 'chase', 'wellsfargo']
    tlds = ['.com', '.net', '.org', '.info', '.online', '.xyz', '.site', '.me', '.co', '.biz']
    suspicious_words = ['secure', 'login', 'verify', 'account', 'update', 'confirm', 'signin', 'service']
    
    urls = []
    for _ in range(n):
        domain = np.random.choice(legitimate_domains)
        tld = np.random.choice(tlds)
        suspicious = np.random.choice(suspicious_words)
        
        # Generate URLs with varying levels of suspiciousness
        suspiciousness_level = np.random.random()  # 0 to 1
        
        if suspiciousness_level > 0.8:  # Highly suspicious (20% of cases)
            pattern = np.random.choice([
                f'http://{domain}-{suspicious}-verify{tld}',
                f'http://secure-{domain}-{suspicious}{tld}',
                f'http://{domain}-account-verify{tld}',
                f'http://{suspicious}-{domain}-secure{tld}'
            ])
        elif suspiciousness_level > 0.5:  # Moderately suspicious (30% of cases)
            pattern = np.random.choice([
                f'http://{domain}.{suspicious}{tld}',
                f'http://{domain}-{suspicious}{tld}',
                f'http://{domain}account{tld}',
                f'http://my-{domain}-{suspicious}{tld}'
            ])
        else:  # Slightly suspicious (50% of cases)
            pattern = np.random.choice([
                f'http://www.{domain}{tld}/{suspicious}',
                f'http://{domain}{tld}/account/{suspicious}',
                f'http://{domain}-online{tld}',
                f'http://{domain}{tld}/login'
            ])
        
        # Add random numbers sometimes (but less frequently)
        if np.random.random() < 0.2:  # Reduced from 0.4
            random_num = np.random.randint(100, 999)
            pattern = pattern.replace(tld, f'{random_num}{tld}')
        
        urls.append(pattern)
    
    return urls

def generate_legitimate_urls(n=1000):
    """Generate legitimate URLs with some borderline cases"""
    legitimate_urls = [
        'https://www.paypal.com/signin',
        'https://www.amazon.com/login',
        'https://www.apple.com/shop',
        'https://www.microsoft.com/account',
        'https://www.google.com/account',
        'https://www.facebook.com/login',
        'https://www.netflix.com/browse',
        'https://www.chase.com/personal/banking',
        'https://www.wellsfargo.com/online-banking',
        'https://www.bankofamerica.com'
    ]
    
    # Generate variations of legitimate URLs
    urls = []
    for base_url in legitimate_urls:
        domain = base_url.split('/')[2]
        base_domain = '.'.join(domain.split('.')[-2:])  # e.g., 'paypal.com'
        
        # Standard paths that might look slightly suspicious but are legitimate
        paths = [
            '',
            '/login',
            '/signin',
            '/account',
            '/secure',
            '/auth',
            '/verify-account',  # Legitimate but could look suspicious
            '/password-reset',
            '/2fa/verify',
            '/security-check'
        ]
        
        # Add variations
        for _ in range(n // len(legitimate_urls)):
            if np.random.random() > 0.7:  # 30% slightly suspicious but legitimate
                path = np.random.choice(paths)
                param = np.random.choice(['?auth=1', '?secure=true', '?verify=1', ''])
                subdomain = np.random.choice(['www', 'secure', 'login', 'auth', 'accounts'])
                url = f'https://{subdomain}.{base_domain}{path}{param}'
            else:  # 70% clearly legitimate
                path = np.random.choice(paths[:5])  # Use only clearly legitimate paths
                param = np.random.choice(['', '?lang=en', '?region=us', '?src=web'])
                url = f'https://www.{base_domain}{path}{param}'
            urls.append(url)
    
    return urls[:n]

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("Generating training data...")
    
    # Generate balanced dataset
    phishing_urls = generate_phishing_urls(2000)  # Reduced from 3000
    legitimate_urls = generate_legitimate_urls(2000)  # Reduced from 3000
    
    # Create dataframes
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
    history = model.train(X_train, y_train, X_val, y_val, epochs=15, batch_size=32)  # Reduced epochs
    
    # Evaluate model
    print("\nEvaluating model...")
    metrics = model.evaluate(X_test, y_test)
    print(f"\nTest Results:")
    print(f"Loss: {metrics[0]:.4f}")
    print(f"Accuracy: {metrics[1]:.4f}")
    print(f"Precision: {metrics[2]:.4f}")
    print(f"Recall: {metrics[3]:.4f}")
    print(f"AUC: {metrics[4]:.4f}")
    
    # Save model and tokenizer
    print("\nSaving model and tokenizer...")
    model.save('data/url_model.h5', 'data/tokenizer.pkl')
    
    print("Done!")

if __name__ == "__main__":
    main() 