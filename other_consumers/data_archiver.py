import json
import csv
import os
import logging
from kafka import KafkaConsumer
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataArchiver:
    def __init__(self, archive_dir='../data'):
        self.archive_dir = archive_dir
        os.makedirs(archive_dir, exist_ok=True)
        
        # Setup Kafka consumer
        self.consumer = KafkaConsumer(
            'processed-data',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='data-archiver',
            auto_offset_reset='latest'
        )
        
        # CSV files for each machine
        self.csv_files = {}
        self.csv_writers = {}
    
    def get_csv_writer(self, machine_id):
        """Get or create CSV writer for a machine"""
        if machine_id not in self.csv_files:
            # Create CSV file
            filename = os.path.join(self.archive_dir, f"{machine_id}_data.csv")
            file_exists = os.path.exists(filename)
            
            csv_file = open(filename, 'a', newline='')
            writer = csv.writer(csv_file)
            
            # Write header if new file
            if not file_exists:
                writer.writerow([
                    'timestamp', 'machine_id', 'temperature', 'vibration', 'rpm',
                    'pressure', 'humidity', 'power_consumption', 'ml_detected_anomaly',
                    'anomaly_score', 'severity'
                ])
            
            self.csv_files[machine_id] = csv_file
            self.csv_writers[machine_id] = writer
        
        return self.csv_writers[machine_id]
    
    def run(self):
        """Main archiving loop"""
        logger.info("Starting data archiver...")
        
        try:
            for message in self.consumer:
                data = message.value
                machine_id = data['machine_id']
                
                # Get CSV writer for this machine
                writer = self.get_csv_writer(machine_id)
                
                # Write data row
                original_data = data['original_data']
                writer.writerow([
                    data['timestamp'],
                    machine_id,
                    original_data['temperature'],
                    original_data['vibration'],
                    original_data['rpm'],
                    original_data['pressure'],
                    original_data['humidity'],
                    original_data['power_consumption'],
                    data['ml_detected_anomaly'],
                    data['anomaly_score'],
                    data.get('severity', 'LOW')
                ])
                
                # Flush to ensure data is written
                self.csv_files[machine_id].flush()
                
                logger.info(f"Archived data for {machine_id}")
        
        except KeyboardInterrupt:
            logger.info("Stopping data archiver...")
        finally:
            # Close all CSV files
            for csv_file in self.csv_files.values():
                csv_file.close()
            self.consumer.close()

if __name__ == "__main__":
    archiver = DataArchiver()
    archiver.run()
