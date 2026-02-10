from pyspark.sql import SparkSession
from pyspark.sql.functions import col


# 1. Create Spark session (this = Driver)
spark = (
    SparkSession.builder
    .appName("Kafka-PySpark-Streaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# 2. Read from Kafka as a STREAM
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "tweets")
    .option("startingOffsets", "latest")
    .load()
)
#

# 3. Kafka values are bytes → cast to string
messages = kafka_df.select(
    col("value").cast("string").alias("message")
)


# JDBC write logic (executed per micro-batch)
def write_to_postgres(batch_df, batch_id):
    (
        batch_df.write
        .format("jdbc")
        .option("url", "jdbc:postgresql://sentiments:5432/realtime_sentiments_analysis")
        .option("dbtable", "raw_tweets")
        .option("user", "admin")
        .option("password", "adminpassword")
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )


# 4. Define the streaming output (console sink)
query = (
    messages.writeStream
    .foreachBatch(write_to_postgres)
    .outputMode("append")
    .start()
)

# 5. Keep the stream running
query.awaitTermination()
