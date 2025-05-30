import json
import logging
from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
import numpy as np
from train_model import AnomalyDetectionModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeAnomalyDetector:
    def __init__(self):
        # Load trained model
        self.model = AnomalyDetectionModel()
        self.model.load_model()
        
        # Setup Kafka consumer and producer
        self.consumer = KafkaConsumer(
            'sensor-data',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='ml-anomaly-detector'
        )
        
        # Fixed producer with custom serializer
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=self._json_serializer
        )
    
    def _json_serializer(self, obj):
        """Custom JSON serializer that handles numpy types"""
        def default_handler(o):
            if isinstance(o, np.bool_):
                return bool(o)
            elif isinstance(o, np.integer):
                return int(o)
            elif isinstance(o, np.floating):
                return float(o)
            elif isinstance(o, np.ndarray):
                return o.tolist()
            elif hasattr(o, 'item'):  # Handle numpy scalars
                return o.item()
            else:
                raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')
        
        return json.dumps(obj, default=default_handler).encode('utf-8')
    
    def detect_anomaly(self, sensor_data):
        """Detect anomaly in real-time sensor data"""
        try:
            # Extract features
            features = [sensor_data.get(col, 0) for col in self.model.feature_columns]
            features_df = pd.DataFrame([features], columns=self.model.feature_columns)
            
            # Scale features
            features_scaled = self.model.scaler.transform(features_df)
            
            # Predict
            prediction = self.model.model.predict(features_scaled)[0]
            anomaly_score = self.model.model.decision_function(features_scaled)[0]
            
            # Convert numpy types to Python types
            is_anomaly = bool(prediction == -1)
            anomaly_score = float(anomaly_score)
            
            return is_anomaly, anomaly_score
        
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return False, 0.0
    
    def _make_json_serializable(self, obj):
        """Convert object to JSON serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        return obj
    
    def run(self):
        """Main inference loop"""
        logger.info("Starting real-time anomaly detection...")
        
        try:
            for message in self.consumer:
                sensor_data = message.value
                machine_id = sensor_data.get('machine_id')
                
                # Detect anomaly
                is_anomaly, anomaly_score = self.detect_anomaly(sensor_data)
                
                # Create result - ensure all values are JSON serializable
                result = {
                    'machine_id': str(machine_id) if machine_id else None,
                    'timestamp': sensor_data.get('timestamp'),
                    'original_data': self._make_json_serializable(sensor_data),
                    'ml_detected_anomaly': bool(is_anomaly),
                    'anomaly_score': float(anomaly_score),
                    'severity': 'HIGH' if anomaly_score < -0.5 else 'MEDIUM' if anomaly_score < -0.2 else 'LOW'
                }
                
                # Send to anomalies topic if anomaly detected
                if is_anomaly:
                    try:
                        self.producer.send('anomalies', value=result)
                        logger.warning(f"ANOMALY DETECTED for {machine_id}: score={anomaly_score:.3f}")
                    except Exception as e:
                        logger.error(f"Error sending to anomalies topic: {e}")
                
                # Always send to processed-data topic
                try:
                    self.producer.send('processed-data', value=result)
                    if not is_anomaly:
                        logger.info(f"Normal reading for {machine_id}: score={anomaly_score:.3f}")
                except Exception as e:
                    logger.error(f"Error sending to processed-data topic: {e}")
                    logger.error(f"Result that failed: {result}")
        
        except KeyboardInterrupt:
            logger.info("Stopping anomaly detection...")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.consumer.close()
            self.producer.close()

if __name__ == "__main__":
    detector = RealTimeAnomalyDetector()
    detector.run()
