#!/usr/bin/env bash
set -e

DETACHED=false
INSTALL_DEPS=true

# -------- Parse flags --------
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -d|--detached)
      DETACHED=true
      shift
      ;;
    -nd|--no-dependancy)
      INSTALL_DEPS=false
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# -------- Config --------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up two levels: scripts/spark -> scripts -> project_root
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
STREAMING_SCRIPT="$PROJECT_ROOT/spark/streaming/run_streaming_spark.py"

SPARK_MASTER="spark://spark-master:7077"
APP_PATH="/opt/spark/work-dir/run_streaming_spark.py"

SPARK_VERSION="3.5.1"
SCALA_VERSION="2.12"

KAFKA_PACKAGE="org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION}"
POSTGRES_PACKAGE="org.postgresql:postgresql:42.7.3"

echo "Deploying Spark Structured Streaming job"
echo "Spark version : ${SPARK_VERSION}"
echo "Scala version : ${SCALA_VERSION}"
echo "Detached mode : ${DETACHED}"

# -------- Check if containers are running --------
echo ""
echo "Checking if Spark containers are running..."
if ! sudo docker ps | grep -q spark-master; then
    echo "ERROR: spark-master container is not running."
    exit 1
fi
echo "✓ Spark containers are running"

# -------- Install dependencies --------
if [ "$INSTALL_DEPS" = true ]; then
  echo ""
  echo "Installing numpy and pandas on Spark Master and Worker..."
  sudo docker exec --user root spark-master pip install numpy pandas --quiet 2>/dev/null || true
  sudo docker exec --user root spark-worker pip install numpy pandas --quiet 2>/dev/null || true
  echo "✓ dependencies installed"
else
  echo ""
  echo "Skipping dependency installation (--no-dependancy flag used)"
fi

# -------- Copy streaming script --------
echo ""
echo "Copying streaming script to Spark Master..."
sudo docker cp "$STREAMING_SCRIPT" spark-master:${APP_PATH}
echo "✓ Streaming script copied to ${APP_PATH}"

# -------- Execution mode --------
echo ""
if [ "$DETACHED" = true ]; then
  echo "Running in DETACHED mode"
  DOCKER_EXEC_FLAGS="-d"
else
  echo "Running in FOREGROUND mode"
  DOCKER_EXEC_FLAGS="-it"
fi

# -------- Run Spark --------
echo ""
echo "Submitting Spark Structured Streaming job..."
echo "================================================================"
sudo docker exec ${DOCKER_EXEC_FLAGS} spark-master \
  /opt/spark/bin/spark-submit \
    --master ${SPARK_MASTER} \
    --conf spark.jars.ivy=/tmp/ivy \
    --packages ${KAFKA_PACKAGE},${POSTGRES_PACKAGE} \
    ${APP_PATH}

echo "================================================================"
echo "Spark submit command issued"
