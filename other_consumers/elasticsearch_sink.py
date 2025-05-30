import json
import logging
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchSink:
    def __init__(self):
        # Connect to Elasticsearch with retry logic
        self.es = self.connect_elasticsearch()
        
        # Setup Kafka consumer
        self.consumer = KafkaConsumer(
            'processed-data',
            'anomalies',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='elasticsearch-sink',
            auto_offset_reset='latest'
        )
        
        # Create indices if they don't exist
        if self.es:
            self.setup_indices()
    
    def connect_elasticsearch(self, max_retries=5):
        """Connect to Elasticsearch with retry logic"""
        for attempt in range(max_retries):
            try:
                es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
                # Test connection
                es.info()
                logger.info("Connected to Elasticsearch")
                return es
            except ConnectionError as e:
                logger.warning(f"Failed to connect to Elasticsearch (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    logger.error("Could not connect to Elasticsearch after all retries")
                    return None
    
    def setup_indices(self):
        """Create Elasticsearch indices with proper mappings"""
        if not self.es:
            return
            
        sensor_mapping = {
            "mappings": {
                "properties": {
                    "machine_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "temperature": {"type": "float"},
                    "vibration": {"type": "float"},
                    "rpm": {"type": "integer"},
                    "pressure": {"type": "float"},
                    "humidity": {"type": "float"},
                    "power_consumption": {"type": "float"},
                    "ml_detected_anomaly": {"type": "boolean"},
                    "anomaly_score": {"type": "float"},
                    "severity": {"type": "keyword"}
                }
            }
        }
        
        anomaly_mapping = {
            "mappings": {
                "properties": {
                    "machine_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "anomaly_score": {"type": "float"},
                    "severity": {"type": "keyword"},
                    "original_data": {
                        "properties": {
                            "temperature": {"type": "float"},
                            "vibration": {"type": "float"},
                            "rpm": {"type": "integer"},
                            "pressure": {"type": "float"},
                            "humidity": {"type": "float"},
                            "power_consumption": {"type": "float"}
                        }
                    }
                }
            }
        }
        
        # Create indices
        try:
            if not self.es.indices.exists(index="sensor-data"):
                self.es.indices.create(index="sensor-data", body=sensor_mapping)
                logger.info("Created sensor-data index")
            
            if not self.es.indices.exists(index="anomalies"):
                self.es.indices.create(index="anomalies", body=anomaly_mapping)
                logger.info("Created anomalies index")
        except RequestError as e:
            logger.error(f"Error creating indices: {e}")
    
    def run(self):
        """Main consumer loop"""
        logger.info("Starting Elasticsearch sink...")
        
        if not self.es:
            logger.error("Elasticsearch not available. Exiting.")
            return
        
        try:
            for message in self.consumer:
                topic = message.topic
                data = message.value
                
                # Add document ID and timestamp
                doc_id = f"{data['machine_id']}_{int(datetime.now().timestamp() * 1000)}"
                
                try:
                    if topic == 'processed-data':
                        # Flatten the data structure
                        doc = {
                            'machine_id': data['machine_id'],
                            'timestamp': data['timestamp'],
                            'ml_detected_anomaly': data['ml_detected_anomaly'],
                            'anomaly_score': data['anomaly_score'],
                            'severity': data.get('severity', 'LOW'),
                            **data['original_data']  # Flatten original_data
                        }
                        
                        # Index to sensor-data
                        self.es.index(index="sensor-data", id=doc_id, body=doc)
                        logger.info(f"Indexed sensor data for {data['machine_id']}")
                    
                    elif topic == 'anomalies':
                        # Index to anomalies
                        self.es.index(index="anomalies", id=doc_id, body=data)
                        logger.info(f"Indexed anomaly for {data['machine_id']}")
                
                except Exception as e:
                    logger.error(f"Error indexing document: {e}")
        
        except KeyboardInterrupt:
            logger.info("Stopping Elasticsearch sink...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    sink = ElasticsearchSink()
    sink.run()
