import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import load_model
from model import extract_url_features
import matplotlib.pyplot as plt
import seaborn as sns

def load_test_data(test_csv):
    """Load test data"""
    test_df = pd.read_csv(test_csv)
    return test_df

def main():
    # Load the model
    print("Loading model...")
    url_model = load_model('data/url_model.h5')
    
    # Load test data
    print("Loading test data...")
    test_data = load_test_data('data/test_urls.csv')
    
    # Extract features
    print("Extracting features...")
    features = []
    for url in test_data['url']:
        features.append(extract_url_features(url))
    
    features_df = pd.DataFrame(features)
    
    # Make predictions
    print("Making predictions...")
    X_test = features_df.to_numpy()
    y_test = test_data['label'].values
    
    y_pred_prob = url_model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    
    # Evaluate
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig('data/confusion_matrix.png')
    
    # Feature importance (for interpretability)
    print("Analyzing feature importance...")
    # This is a simple approach - for a real project you might use SHAP values or other methods
    weights = url_model.layers[0].get_weights()[0]
    feature_importance = np.abs(weights).mean(axis=1)
    
    feature_names = features_df.columns
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    }).sort_values('Importance', ascending=False)
    
    print("Top 5 important features:")
    print(importance_df.head(5))
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=importance_df.head(10))
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.savefig('data/feature_importance.png')
    
    print("Evaluation complete!")

if __name__ == "__main__":
    main() 