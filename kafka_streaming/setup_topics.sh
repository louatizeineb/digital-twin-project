#!/bin/bash

echo "Creating Kafka topics..."

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 30

# Function to check if Kafka is ready
check_kafka() {
    docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null
    return $?
}

# Wait for Kafka to be ready (up to 60 seconds)
for i in {1..12}; do
    if check_kafka; then
        echo "Kafka is ready!"
        break
    else
        echo "Waiting for Kafka... attempt $i/12"
        sleep 5
    fi
done

# Create topics
echo "Creating sensor-data topic..."
docker exec kafka kafka-topics --create --topic sensor-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists

echo "Creating processed-data topic..."
docker exec kafka kafka-topics --create --topic processed-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists

echo "Creating anomalies topic..."
docker exec kafka kafka-topics --create --topic anomalies --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists

# List topics to verify
echo "Current Kafka topics:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

echo "Kafka topics created successfully!"
