# Distributed Sentiment Model Training with PySpark

This module handles the training of the Sentiment Analysis model using Apache Spark (PySpark). It scales the training process, allowing for handling simpler datasets locally or large-scale datasets in a distributed cluster.

## Files

- **`train_sentiment_spark.py`**: The main PySpark script. It transforms raw text data (using TF-IDF) and trains a Logistic Regression model.

## Setup & Prerequisites

Ensure your Docker containers are running:
```bash
docker-compose -f infra/docker-compose.yaml up -d
```

### 1. Install Python Dependencies
The default `apache/spark` image might not include `numpy` by default, which is required for PySpark ML operations. You need to install it on the **Spark Master** (and Workers if strictly needed, though usually the driver handles the heavy python logic for this specific small script, workers need it for UDFs/vector operations).

```bash
# Install numpy on Spark Master
sudo docker exec -it spark-master pip install numpy

# Install numpy on Spark Worker (good practice for distributed tasks)
sudo docker exec -it spark-worker pip install numpy
```

### 2. Copy Dataset and Script
Since we are running in a containerized environment, we need to move the data and the script into the container.

**Note:** In a distributed setup using `file:///` paths, the data file must exist at the same path on **all nodes** (Master and Workers).

```bash
# Copy dataset to Spark Master
sudo docker cp data/cleaned.csv spark-master:/opt/

# Copy dataset to Spark Worker (Crucial for distributed reading)
sudo docker cp data/cleaned.csv spark-worker:/opt/

# Copy the training script to Spark Master
sudo docker cp spark/training/train_sentiment_spark.py spark-master:/tmp/
```

## Running the Training Job

Submit the job to the Spark Master using `spark-submit`.

```bash
sudo docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/train_sentiment_spark.py
```

## Output
- The script will print evaluation metrics (Accuracy, F1 Score) to the console.
- The trained model will be saved inside the container at `/opt/spark_sentiment_model`.

### Retrieving the Model
To use this model in your application, copy it back to your host machine:

```bash
# Copy the model folder from the container to your local 'ml/' directory
sudo docker cp spark-master:/opt/spark_sentiment_model ./ml/
```

## Troubleshooting
- **ModuleNotFoundError: No module named 'numpy'**: Ensure you ran the `pip install numpy` command in step 1.
- **AnalysisException: Path does not exist**: Ensure `cleaned.csv` is copied to **BOTH** `spark-master` and `spark-worker` at `/opt/`.
