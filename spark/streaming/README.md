# Spark Streaming Job

This directory contains the PySpark application responsible for consuming tweet data from Kafka in real-time and persisting it to PostgreSQL.

## Overview

The `app.py` script sets up a Spark Structured Streaming job that:
1.  Connects to the Kafka broker.
2.  Subscribes to the `tweets` topic.
3.  Processes the stream (currently casts raw bytes to string).
4.  Writes the data to a PostgreSQL database table named `raw_tweets`.

## Prerequisites

Ensure your infrastructure stack is running:
- Kafka Broker (on `broker:9092`)
- Spark Master & Worker
- PostgreSQL (reachable as `sentiments` or configured host)

## Deployment

Since Spark is running in a Docker container, you need to copy the Python script into the Spark Master container before executing it.

### 1. Copy the Application to the Container

Run the following command from this directory:

```bash
docker cp app.py spark-master:/tmp/
```

### 2. Submit the Spark Job

**Option A: Using the Helper Script (Recommended)**

A helper script is available to simplify running the job. It handles the `spark-submit` arguments for you.

```bash
# From the project root
./scripts/run-streaming.sh
```

Flags:
- `-d` or `--detached`: Run in detached mode (background).

**Option B: Manual Submission**

Execute the job using `spark-submit` inside the container. This command handles downloading the necessary dependencies (Spark-Kafka integration and PostgreSQL driver) via Maven coordinates.

```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/ivy \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3 \
  /tmp/app.py
```

## Dependencies

The job automatically pulls the following JARs:
- `spark-sql-kafka-0-10_2.12` (v3.5.1): For Kafka integration.
- `postgresql` (v42.7.3): JDBC driver for database connectivity.