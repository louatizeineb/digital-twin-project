# 🏭 Smart Factory Digital Twin for Predictive Maintenance

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![Kafka](https://img.shields.io/badge/Apache-Kafka-orange.svg)](https://kafka.apache.org)
[![NiFi](https://img.shields.io/badge/Apache-NiFi-green.svg)](https://nifi.apache.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive digital twin system that simulates a smart factory environment with real-time sensor data streaming, anomaly detection, and predictive maintenance capabilities. This project demonstrates modern data engineering practices using Apache Kafka, NiFi, machine learning, and containerized microservices.

## 🎯 Project Overview

This digital twin system creates a virtual representation of a factory floor where physical machines send sensor data (temperature, vibration, RPM) to a central platform. The system processes this data in real-time to detect anomalies and predict maintenance needs before equipment failures occur.

### Key Features

- **Real-time Data Simulation**: Simulates multiple factory machines with realistic sensor readings
- **Stream Processing**: Uses Apache Kafka for high-throughput data streaming
- **Data Ingestion**: Apache NiFi for flexible data flow management
- **ML-Powered Analytics**: Anomaly detection using machine learning algorithms
- **Live Dashboard**: Real-time visualization of machine health and alerts
- **Scalable Architecture**: Containerized microservices for easy deployment
- **Multiple Data Sinks**: Support for Elasticsearch, MongoDB, and other storage systems

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Sensor Data    │───▶│   Apache NiFi   │───▶│  Apache Kafka   │
│   Simulator     │    │   (Ingestion)   │    │  (Streaming)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                        ┌─────────────────────────────────┼─────────────────────────────────┐
                        │                                 │                                 │
                        ▼                                 ▼                                 ▼
            ┌─────────────────┐              ┌─────────────────┐                ┌─────────────────┐
            │   ML Anomaly    │              │   Dashboard     │                │   Other Data    │
            │   Detection     │              │   Application   │                │   Consumers     │
            └─────────────────┘              └─────────────────┘                └─────────────────┘
```

## 📁 Project Structure

```
smart-factory-digital-twin/
├── sensor_simulator/           # Simulates factory sensor data
│   ├── generator.py
│   ├── config.json
│   └── README.md
├── ingestion/                  # Apache NiFi configuration
│   ├── nifi_flow_template.xml
│   └── setup_nifi.sh
├── kafka_streaming/            # Kafka producers and consumers
│   ├── producer.py
│   ├── consumer.py
│   └── kafka_config/
│       └── server.properties
├── ml_anomaly_detection/       # Machine learning models
│   ├── model/
│   │   └── model.pkl
│   ├── train_model.py
│   ├── inference.py
│   └── requirements.txt
├── dashboard_app/              # Web dashboard
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── other_consumers/            # Additional data sinks
│   └── elasticsearch_sink.py
├── docker/                     # Container orchestration
│   ├── docker-compose.yml
│   └── kafka/
│       └── Dockerfile
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-factory-digital-twin.git
   cd smart-factory-digital-twin
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the infrastructure**
   ```bash
   cd docker
   docker-compose up -d
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Train the ML model** (optional - pre-trained model included)
   ```bash
   cd ml_anomaly_detection
   python train_model.py
   ```

6. **Start the sensor simulator**
   ```bash
   cd sensor_simulator
   python generator.py
   ```

7. **Launch the dashboard**
   ```bash
   cd dashboard_app
   python app.py
   ```

8. **Access the services**
   - Dashboard: http://localhost:5000
   - NiFi UI: http://localhost:8080/nifi
   - Kafka Manager: http://localhost:9000

## 🔧 Configuration

### Sensor Simulator Configuration

Edit `sensor_simulator/config.json` to customize:
- Number of machines
- Sensor types and ranges
- Data generation frequency
- Output format

```json
{
  "machines": [
    {
      "id": "M001",
      "sensors": {
        "temperature": {"min": 60, "max": 100},
        "vibration": {"min": 0.1, "max": 1.5},
        "rpm": {"min": 1000, "max": 5000}
      }
    }
  ],
  "interval_seconds": 2
}
```

### Kafka Topics

The system uses the following Kafka topics:
- `sensor-data`: Raw sensor readings
- `anomalies`: Detected anomalies
- `alerts`: Critical alerts requiring immediate attention

## 🤖 Machine Learning

### Anomaly Detection

The system uses an Isolation Forest algorithm to detect anomalies in sensor data. The model considers multiple factors:
- Temperature spikes or drops
- Unusual vibration patterns
- RPM irregularities
- Correlation between different sensors

### Model Training

```bash
cd ml_anomaly_detection
python train_model.py --data-path ../data/training_data.csv
```

### Real-time Inference

The ML consumer continuously processes incoming sensor data and flags anomalies in real-time.

## 📊 Dashboard Features

- **Real-time Metrics**: Live sensor readings from all machines
- **Anomaly Alerts**: Immediate notifications for detected issues
- **Historical Trends**: Time-series visualization of sensor data
- **Machine Health Score**: Overall health assessment for each machine
- **Predictive Insights**: Estimated time to next maintenance

## 🐳 Docker Deployment

### Services Included

- **Zookeeper**: Kafka coordination
- **Kafka**: Message streaming
- **NiFi**: Data ingestion and routing
- **Elasticsearch**: Data storage and search
- **Dashboard App**: Web interface
- **ML Service**: Anomaly detection

### Scaling

Scale individual services:
```bash
docker-compose up -d --scale kafka-consumer=3
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

### Test Categories

- Unit tests for individual components
- Integration tests for data flow
- Performance tests for streaming capacity
- End-to-end system tests

## 📈 Performance Considerations

- **Throughput**: Handles 10,000+ messages per second
- **Latency**: Sub-second anomaly detection
- **Scalability**: Horizontally scalable consumers
- **Fault Tolerance**: Built-in redundancy and recovery

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Simulation** | Python, JSON |
| **Ingestion** | Apache NiFi |
| **Streaming** | Apache Kafka |
| **ML Detection** | scikit-learn, PyTorch |
| **Visualization** | Flask, Chart.js |
| **Storage** | Elasticsearch, MongoDB |
| **Containerization** | Docker, Docker Compose |

## 🔍 Monitoring & Observability

- **Kafka Metrics**: Message throughput, consumer lag
- **Application Metrics**: Processing time, error rates
- **System Metrics**: CPU, memory, disk usage
- **Custom Dashboards**: Grafana integration available

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run linting
flake8 .

# Run formatting
black .
```

## 📝 Use Cases

- **Manufacturing**: Predictive maintenance for production equipment
- **Energy**: Monitoring power plant machinery
- **Automotive**: Assembly line optimization
- **Aerospace**: Aircraft component health monitoring
- **Oil & Gas**: Pipeline and refinery equipment tracking


