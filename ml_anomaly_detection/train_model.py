import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetectionModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        self.feature_columns = [
            'temperature', 'vibration', 'rpm', 
            'pressure', 'humidity', 'power_consumption'
        ]
    
    def generate_training_data(self, n_samples=10000):
        """Generate synthetic training data"""
        data = []
        
        for _ in range(n_samples):
            # Normal data (90%)
            if np.random.random() > 0.1:
                record = {
                    'temperature': np.random.normal(75, 8),
                    'vibration': np.random.normal(0.6, 0.3),
                    'rpm': np.random.normal(2500, 800),
                    'pressure': np.random.normal(20, 3),
                    'humidity': np.random.normal(50, 10),
                    'power_consumption': np.random.normal(100, 20),
                    'is_anomaly': False
                }
            # Anomalous data (10%)
            else:
                record = {
                    'temperature': np.random.choice([
                        np.random.normal(110, 5),  # Overheating
                        np.random.normal(40, 5)    # Too cold
                    ]),
                    'vibration': np.random.normal(3, 0.5),  # High vibration
                    'rpm': np.random.choice([
                        np.random.normal(500, 100),   # Too slow
                        np.random.normal(5500, 200)   # Too fast
                    ]),
                    'pressure': np.random.normal(5, 2),  # Low pressure
                    'humidity': np.random.normal(90, 5),  # High humidity
                    'power_consumption': np.random.normal(200, 30),  # High consumption
                    'is_anomaly': True
                }
            
            data.append(record)
        
        return pd.DataFrame(data)
    
    def train(self, df=None):
        """Train the anomaly detection model"""
        if df is None:
            logger.info("Generating synthetic training data...")
            df = self.generate_training_data()
        
        # Prepare features
        X = df[self.feature_columns]
        
        # Handle any NaN values
        X = X.fillna(X.mean())
        
        # Scale features
        logger.info("Scaling features...")
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        logger.info("Training Isolation Forest model...")
        self.model.fit(X_scaled)
        
        # Evaluate on training data
        predictions = self.model.predict(X_scaled)
        anomaly_score = self.model.decision_function(X_scaled)
        
        # Convert predictions (-1 for anomaly, 1 for normal)
        predictions = (predictions == -1)
        
        logger.info(f"Training completed. Detected {predictions.sum()} anomalies out of {len(df)} samples")
        
        return predictions, anomaly_score
    
    def save_model(self, model_path='model/'):
        """Save trained model and scaler"""
        import os
        os.makedirs(model_path, exist_ok=True)
        
        joblib.dump(self.model, f'{model_path}/isolation_forest.pkl')
        joblib.dump(self.scaler, f'{model_path}/scaler.pkl')
        
        # Save feature columns
        with open(f'{model_path}/feature_columns.json', 'w') as f:
            json.dump(self.feature_columns, f)
        
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path='model/'):
        """Load trained model and scaler"""
        self.model = joblib.load(f'{model_path}/isolation_forest.pkl')
        self.scaler = joblib.load(f'{model_path}/scaler.pkl')
        
        with open(f'{model_path}/feature_columns.json', 'r') as f:
            self.feature_columns = json.load(f)
        
        logger.info(f"Model loaded from {model_path}")

if __name__ == "__main__":
    # Train and save model
    model = AnomalyDetectionModel()
    model.train()
    model.save_model()
    logger.info("Model training completed!")
