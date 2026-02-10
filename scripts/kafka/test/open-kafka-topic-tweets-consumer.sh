#!/bin/bash

# Script to verify Kafka streaming by consuming from the 'tweets' topic
# This opens a console consumer inside the Kafka container

echo "Opening Kafka Console Consumer for topic 'tweets'..."
echo "Press Ctrl+C to exit."
echo "---------------------------------------------------"

# Run kafka-console-consumer inside the 'broker' container
sudo docker exec -it broker /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic tweets \
  --from-beginning

echo ""
echo "Consumer closed."
