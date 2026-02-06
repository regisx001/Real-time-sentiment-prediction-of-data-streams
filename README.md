# Real-time Sentiment Prediction of Data Streams

This project is a real-time data processing pipeline designed for sentiment analysis of data streams, specifically tweets. It utilizes Spring Boot for the core application logic and orchestrates a microservices architecture using Docker Compose.

## Architecture

The system consists of the following components:

- **Core Service**: A Spring Boot application (Java 21) that acts as the entry point for data ingestion.
- **Apache Kafka**: A distributed event streaming platform used for buffering and buffering raw data (tweets).
- **PostgreSQL (TimescaleDB)**: A time-series relational database for persistent storage.
- **Apache Spark**: A unified analytics engine for large-scale data processing (Cluster mode with Master and Worker).
- **pgAdmin**: A web-based administration tool for PostgreSQL.

## Prerequisites

- Java 21+
- Maven
- Docker and Docker Compose

## Getting Started

### 1. Infrastructure Setup

Navigate to the infrastructure directory and start the required services using Docker Compose:

```bash
cd infra
docker-compose up -d
```

This will start:
- **Kafka Broker**: Port 9092
- **TimescaleDB**: Port 5432
- **Spark Master**: Port 8080 (Web UI), 7077 (Master)
- **Spark Worker**: Port 8081 (Web UI)
- **pgAdmin**: Port 5050

### 2. Configuration

The application requires the following environment variables to be set. You can set them in your environment or via a `.env` file if configured.

```
POSTGRES_URL=jdbc:postgresql://localhost:5432/realtime_sentiments_analysis
POSTGRES_USERNAME=admin
POSTGRES_PASSWORD=adminpassword
```

### 3. Build and Run

Return to the project root and build the application:

```bash
./mvnw clean install
```

Run the Spring Boot application:

```bash
./mvnw spring-boot:run
```

The server will start on port `8090`.

## API Usage

### Send a Tweet (Kafka Producer)

Submit a tweet event to the Kafka topic `tweets.raw`.

**Endpoint:** `POST /api/kafka/send`
**Content-Type:** `application/json`

**Example Request:**

```bash
curl -X POST localhost:8090/api/kafka/send \
  -H "Content-Type: application/json" \
  -d '{
        "tweetId": "1",
        "text": "This pipeline finally makes sense",
        "timestamp": 1770165600000
      }'
```

**Success Response:**
```text
Message sent to Kafka
```

## Kafka Consumer

The application creates a debug consumer group `debug-consumer` that listens to `tweets.raw` and prints received messages to the console for verification.

```text
Consumed tweet: TweetEvent[tweetId=1, text=This pipeline finally makes sense, timestamp=1770165600000]
```

## Project Structure

- `src/main/java`: Java source code.
- `src/main/resources`: Configuration files (application.yaml).
- `infra`: Infrastructure definition (docker-compose.yaml).
