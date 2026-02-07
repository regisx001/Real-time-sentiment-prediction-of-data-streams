#!/usr/bin/env bash
set -e

DETACHED=false

# -------- Parse flags --------
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -d|--detached)
      DETACHED=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# -------- Config --------
SPARK_MASTER="spark://spark-master:7077"
APP_PATH="/tmp/app.py"

SPARK_VERSION="3.5.1"
SCALA_VERSION="2.12"

KAFKA_PACKAGE="org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION}"
POSTGRES_PACKAGE="org.postgresql:postgresql:42.7.3"

echo "Deploying Spark Structured Streaming job"
echo "Spark version : ${SPARK_VERSION}"
echo "Scala version : ${SCALA_VERSION}"
echo "Detached mode : ${DETACHED}"

# -------- Execution mode --------
if [ "$DETACHED" = true ]; then
  echo "Running in DETACHED mode"
  DOCKER_EXEC_FLAGS="-d"
else
  echo "Running in FOREGROUND mode"
  DOCKER_EXEC_FLAGS="-it"
fi

# -------- Run Spark --------
docker exec ${DOCKER_EXEC_FLAGS} spark-master \
  /opt/spark/bin/spark-submit \
    --master ${SPARK_MASTER} \
    --conf spark.jars.ivy=/tmp/ivy \
    --packages ${KAFKA_PACKAGE},${POSTGRES_PACKAGE} \
    ${APP_PATH}

echo "Spark submit command issued"
