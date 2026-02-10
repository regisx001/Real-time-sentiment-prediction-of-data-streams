#!/bin/bash

# Script to verify Kafka streaming by consuming from the 'tweets' topic
# This opens a console producer inside the Kafka container

echo "Opening Kafka Console Producer for topic 'tweets'..."
echo "Press Ctrl+C to exit."
echo "---------------------------------------------------"

# Run kafka-console-producer inside the 'broker' container
sudo docker exec -it broker /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic tweets \

echo ""
echo "Producer closed."
