from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
from kafka import KafkaConsumer
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store recent data in memory
recent_data = []
anomalies = []
machine_status = {}

class DashboardDataConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'processed-data',
            'anomalies',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='dashboard-consumer'
        )
    
    def consume_data(self):
        """Consume data from Kafka and update dashboard"""
        global recent_data, anomalies, machine_status
        
        for message in self.consumer:
            topic = message.topic
            data = message.value
            
            if topic == 'processed-data':
                # Update recent data
                recent_data.append(data)
                if len(recent_data) > 1000:  # Keep only last 1000 records
                    recent_data.pop(0)
                
                # Update machine status
                machine_id = data['machine_id']
                machine_status[machine_id] = {
                    'last_update': data['timestamp'],
                    'temperature': data['original_data']['temperature'],
                    'vibration': data['original_data']['vibration'],
                    'rpm': data['original_data']['rpm'],
                    'is_anomaly': data['ml_detected_anomaly'],
                    'anomaly_score': data['anomaly_score'],
                    'severity': data.get('severity', 'LOW')
                }
                
                # Send real-time update to dashboard
                socketio.emit('sensor_update', data)
            
            elif topic == 'anomalies':
                # Store anomaly
                anomalies.append(data)
                if len(anomalies) > 100:  # Keep only last 100 anomalies
                    anomalies.pop(0)
                
                # Send anomaly alert to dashboard
                socketio.emit('anomaly_alert', data)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/machines')
def get_machines():
    return jsonify(machine_status)

@app.route('/api/recent-data')
def get_recent_data():
    # Return last 100 data points
    return jsonify(recent_data[-100:] if recent_data else [])

@app.route('/api/anomalies')
def get_anomalies():
    return jsonify(anomalies)

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to dashboard')
    emit('machine_status', machine_status)

if __name__ == '__main__':
    # Start Kafka consumer in background thread
    consumer = DashboardDataConsumer()
    consumer_thread = threading.Thread(target=consumer.consume_data, daemon=True)
    consumer_thread.start()
    
    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
