#!/bin/bash

# Script to run Spark sentiment model training
# This script handles all setup and execution steps for distributed training

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_FILE="$PROJECT_ROOT/data/cleaned.csv"
SCRIPT_FILE="$PROJECT_ROOT/spark/training/train_sentiment_spark.py"

echo "=== Spark Sentiment Model Training ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# Check if containers are running
echo "Checking if Spark containers are running..."
if ! sudo docker ps | grep -q spark-master; then
    echo "ERROR: spark-master container is not running."
    echo "Start containers with: docker-compose -f infra/docker-compose.yaml up -d"
    exit 1
fi

if ! sudo docker ps | grep -q spark-worker; then
    echo "ERROR: spark-worker container is not running."
    echo "Start containers with: docker-compose -f infra/docker-compose.yaml up -d"
    exit 1
fi

echo "✓ Spark containers are running"
echo ""

# Step 1: Install numpy on Master and Worker
echo "Step 1: Installing numpy on Spark Master and Worker..."
sudo docker exec spark-master pip install numpy --quiet 2>/dev/null || true
sudo docker exec spark-worker pip install numpy --quiet 2>/dev/null || true
echo "✓ numpy installed"
echo ""

# Step 2: Copy data to Master and Worker (writable work-dir)
echo "Step 2: Copying dataset to Spark containers..."
if [ ! -f "$DATA_FILE" ]; then
    echo "ERROR: Dataset not found at $DATA_FILE"
    exit 1
fi

sudo docker cp "$DATA_FILE" spark-master:/opt/spark/work-dir/cleaned.csv
sudo docker cp "$DATA_FILE" spark-worker:/opt/spark/work-dir/cleaned.csv
echo "✓ Dataset copied to Master and Worker work-dir"
echo ""

# Step 3: Copy training script
echo "Step 3: Copying training script to Spark Master..."
sudo docker cp "$SCRIPT_FILE" spark-master:/tmp/train_sentiment_spark.py
echo "✓ Training script copied"
echo ""

# Step 4: Run the training job
echo "Step 4: Submitting training job to Spark cluster..."
echo "================================================================"
sudo docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/train_sentiment_spark.py
echo "================================================================"
echo ""

# Step 5: Copy model back to host
echo "Step 5: Copying trained model back to host..."
mkdir -p "$PROJECT_ROOT/ml"
sudo docker cp spark-master:/opt/spark/work-dir/spark_sentiment_model "$PROJECT_ROOT/ml/" 2>/dev/null || true
echo "✓ Model saved to $PROJECT_ROOT/ml/spark_sentiment_model"
echo ""

echo "=== Training Complete ==="
