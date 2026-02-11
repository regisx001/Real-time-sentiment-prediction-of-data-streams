from pyspark.ml.functions import vector_to_array
from pyspark.sql.functions import expr
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, udf
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
print("Spark Streaming with RANDOM Sentiment (Mock)")
print("=" * 60)

# 2. Read from Kafka as a STREAM
kafka_server = "broker:9092"
print(f"✓ Connecting to Kafka at: {kafka_server}")
print(f"✓ Reading from topic: tweets")
print(f"✓ Writing to topic: processed-tweets")
print("=" * 60)

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_server)
    .option("subscribe", "tweets")
    .option("startingOffsets", "latest")
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


# 4. Generate RANDOM sentiment


# def random_sentiment():
#     """Randomly return POSITIVE or NEGATIVE"""
#     return random.choice(["POSITIVE", "NEGATIVE"])


# def random_score():
#     """Random confidence score between 0.7 and 0.99"""
#     return round(random.uniform(0.7, 0.99), 2)


# # Register UDFs
# sentiment_udf = udf(lambda x: random_sentiment(), StringType())
# score_udf = udf(lambda x: random_score(), DoubleType())

# # Apply random sentiment
# processed_df = parsed_df.withColumn("sentiment", sentiment_udf(col("tweetId")))
# processed_df = processed_df.withColumn("score", score_udf(col("tweetId")))


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
    .option("topic", "processed-tweets")
    .option("checkpointLocation", "/tmp/spark_checkpoint_tweets_mock")
    .outputMode("append")
    .start()
)

print("✓ Streaming job started successfully!")
print("  Waiting for tweets...")
query.awaitTermination()
