import six
import json
import time
import random
import logging
from kafka import KafkaProducer
from datetime import datetime
from confluent_kafka import Producer
from kafka.errors import KafkaError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorSimulator:
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8') if v else None
        )
        
    def generate_sensor_data(self, machine):
        """Generate realistic sensor data with some anomalies"""
        base_temp = random.uniform(
            machine['sensors']['temperature']['min'],
            machine['sensors']['temperature']['max']
        )
        
        # Introduce anomalies 5% of the time
        if random.random() < 0.05:
            temp_anomaly = random.choice([
                base_temp + 30,  # Overheating
                base_temp - 20   # Undercooling
            ])
            vibration_anomaly = random.uniform(2.0, 5.0)  # High vibration
            rpm_anomaly = random.randint(500, 800)  # Low RPM
            
            return {
                'machine_id': machine['id'],
                'timestamp': datetime.now().isoformat(),
                'temperature': round(temp_anomaly, 2),
                'vibration': round(vibration_anomaly, 2),
                'rpm': rpm_anomaly,
                'pressure': round(random.uniform(10, 50), 2),
                'humidity': round(random.uniform(30, 70), 1),
                'power_consumption': round(random.uniform(50, 200), 2),
                'is_anomaly': True
            }
        else:
            return {
                'machine_id': machine['id'],
                'timestamp': datetime.now().isoformat(),
                'temperature': round(base_temp, 2),
                'vibration': round(random.uniform(
                    machine['sensors']['vibration']['min'],
                    machine['sensors']['vibration']['max']
                ), 2),
                'rpm': random.randint(
                    machine['sensors']['rpm']['min'],
                    machine['sensors']['rpm']['max']
                ),
                'pressure': round(random.uniform(15, 25), 2),
                'humidity': round(random.uniform(40, 60), 1),
                'power_consumption': round(random.uniform(80, 120), 2),
                'is_anomaly': False
            }
    
    def run(self):
        """Main simulation loop"""
        logger.info("Starting sensor simulation...")
        
        try:
            while True:
                for machine in self.config['machines']:
                    sensor_data = self.generate_sensor_data(machine)
                    
                    # Send to Kafka
                    future = self.producer.send(
                        'sensor-data',
                        key=machine['id'],
                        value=sensor_data
                    )
                    
                    logger.info(f"Sent data for {machine['id']}: "
                              f"T={sensor_data['temperature']}°C, "
                              f"V={sensor_data['vibration']}, "
                              f"RPM={sensor_data['rpm']}")
                
                time.sleep(self.config['interval_seconds'])
                
        except KeyboardInterrupt:
            logger.info("Stopping sensor simulation...")
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        finally:
            self.producer.close()

if __name__ == "__main__":
    simulator = SensorSimulator()
    simulator.run()
