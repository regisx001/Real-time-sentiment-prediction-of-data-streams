from pyspark.ml.functions import vector_to_array
from pyspark.sql.functions import expr
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, udf, lower, regexp_replace
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType
import random

# 1. Create Spark session
spark = (
    SparkSession.builder
    .appName("Kafka-PySpark-Streaming-MockSentiment")
    .master("local[*]")
    .config("spark.shuffle.service.enabled", "false")
    .config("spark.dynamicAllocation.enabled", "false")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


model_path = "/opt/spark/work-dir/spark_sentiment_model"
model = PipelineModel.load(model_path)

print("✓ Model loaded successfully")


print("=" * 60)
print("Spark Streaming with TRAINED Sentiment Model")
print("=" * 60)

# 2. Read from Kafka as a STREAM
kafka_server = "broker:9092"
print(f"✓ Connecting to Kafka at: {kafka_server}")
print(f"✓ Reading from topic: tweets.raw")
print(f"✓ Writing to topic: tweets.processed")
print("=" * 60)

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_server)
    .option("subscribe", "tweets.raw")
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")
    .load()
)

# 3. Process Data - Parse incoming JSON
schema = StructType([
    StructField("tweetId", StringType()),
    StructField("text", StringType()),
    StructField("timestamp", LongType())
])

messages = kafka_df.select(
    col("value").cast("string").alias("json_string")
)

parsed_df = messages.select(
    from_json(col("json_string"), schema).alias("data")
).select("data.*")

parsed_df = parsed_df.withColumnRenamed("text", "cleaned_text")

# Apply cleaning steps matching training pipeline
parsed_df = parsed_df.withColumn("cleaned_text", lower(col("cleaned_text")))
parsed_df = parsed_df.withColumn(
    "cleaned_text", regexp_replace(col("cleaned_text"), r"http\S+", ""))
parsed_df = parsed_df.withColumn(
    "cleaned_text", regexp_replace(col("cleaned_text"), r"@\w+", ""))
parsed_df = parsed_df.withColumn("cleaned_text", regexp_replace(
    col("cleaned_text"), r"[^a-zA-Z\s]", ""))
parsed_df = parsed_df.withColumn(
    "cleaned_text", regexp_replace(col("cleaned_text"), r"\s+", " "))

predictions = model.transform(parsed_df)


predictions = predictions.withColumn(
    "prob_array",
    vector_to_array(col("probability"))
)

processed_df = predictions.select(
    col("tweetId"),
    col("predicted_label").alias("sentiment"),
    col("prob_array")[col("prediction").cast("int")].alias("score")
)

# Select output columns
output_df = processed_df.select(
    col("tweetId"),
    col("sentiment"),
    col("score")
)

# Convert to JSON for Kafka
kafka_output = output_df.select(
    to_json(struct(col("tweetId"), col("sentiment"), col("score"))).alias("value")
)

# 5. Write back to Kafka
query = (
    kafka_output.writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_server)
    .option("topic", "tweets.processed")
    .option("checkpointLocation", "/tmp/spark_checkpoint_tweets_mock")
    .outputMode("append")
    .start()
)

print("✓ Streaming job started successfully!")
print("  Waiting for tweets...")
query.awaitTermination()
