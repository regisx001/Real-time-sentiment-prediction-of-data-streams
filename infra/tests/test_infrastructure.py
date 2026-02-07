import psycopg2
from kafka import KafkaAdminClient
import requests
import time
import sys

# Configuration
DB_CONFIG = {
    'dbname': 'dataquality_db',
    'user': 'admin',
    'password': 'adminpassword',
    'host': 'localhost',
    'port': '5432'
}

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
SPARK_MASTER_UI = 'http://localhost:8080'
SPARK_WORKER_UI = 'http://localhost:8081'


def print_status(service, status, message=""):
    color = "\033[92m" if status == "PASS" else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{status}{reset}] {service}: {message}")


def test_timescaledb():
    print("\nTesting TimescaleDB Connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        print_status("TimescaleDB", "PASS",
                     f"Connected! Version: {version.split()[0]}...")
        return True
    except Exception as e:
        print_status("TimescaleDB", "FAIL", str(e))
        return False


def test_kafka():
    print("\nTesting Kafka Connection...")
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        topics = admin_client.list_topics()
        print_status("Kafka", "PASS", f"Connected! Found topics: {topics}")
        return True
    except Exception as e:
        print_status("Kafka", "FAIL", str(e))
        return False


def test_spark_ui():
    print("\nTesting Spark UI Reachability...")
    success = True

    # Check Master
    try:
        response = requests.get(SPARK_MASTER_UI)
        if response.status_code == 200:
            print_status("Spark Master UI", "PASS", "Reachable")
        else:
            print_status("Spark Master UI", "FAIL",
                         f"Status Code: {response.status_code}")
            success = False
    except Exception as e:
        print_status("Spark Master UI", "FAIL", str(e))
        success = False

    # Check Worker
    try:
        response = requests.get(SPARK_WORKER_UI)
        if response.status_code == 200:
            print_status("Spark Worker UI", "PASS", "Reachable")
        else:
            print_status("Spark Worker UI", "FAIL",
                         f"Status Code: {response.status_code}")
            success = False
    except Exception as e:
        print_status("Spark Worker UI", "FAIL", str(e))
        success = False

    return success


def main():
    print("Starting Infrastructure Health Check...")
    print("="*40)

    db_ok = test_timescaledb()
    kafka_ok = test_kafka()
    spark_ok = test_spark_ui()

    print("="*40)
    if db_ok and kafka_ok and spark_ok:
        print("\033[92mAll systems operational!\033[0m")
        sys.exit(0)
    else:
        print("\033[91mSome systems failed check.\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
