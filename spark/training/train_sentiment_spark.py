from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Tokenizer,
    StopWordsRemover,
    CountVectorizer,
    IDF,
    StringIndexer
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import os
from pyspark.ml.feature import IndexToString
from pyspark.sql.functions import col, lower, regexp_replace
from pyspark.sql.functions import regexp_replace, col, lower


def main():
    # 1. SparkSession (Driver Entry Point)
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("SentimentTrainingSparkML") \
        .getOrCreate()

    # Enable Arrow for optimization if available (optional)
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "../../"))

    # Check if data exists in /opt/spark/work-dir (Writable container environment)
    work_dir = "/opt/spark/work-dir"
    if os.path.exists(work_dir):
        # Taking a guess that inside the container we might mount differently or the same
        # Ideally the user would mount ./data:/opt/spark/work-dir/data
        # But looking at previous code it expected cleaned.csv directly in work-dir.
        # Let's assume for now we look for the file in a similar relative path or just flat.

        # If the user copies the whole data folder:
        possible_path = f"{work_dir}/data/twitter/twitter_training.csv"
        if os.path.exists(possible_path):
            data_path = f"file://{possible_path}"
            validation_path = f"file://{work_dir}/data/twitter/twitter_validation.csv"
        else:
            # Fallback if flat
            data_path = f"file://{work_dir}/twitter_training.csv"
            validation_path = f"file://{work_dir}/twitter_validation.csv"

        model_output_path = f"{work_dir}/spark_sentiment_model"
    else:
        # Fallback to local development path
        data_path = os.path.join(
            project_root, "data/twitter/twitter_training.csv")
        validation_path = os.path.join(
            project_root, "data/twitter/twitter_validation.csv")
        model_output_path = os.path.join(
            project_root, "ml/spark_sentiment_model")

    print(f"Loading training data from: {data_path}")
    print(f"Loading validation data from: {validation_path}")

    # 2. Load Data (Distributed)
    # The new dataset has no header and 4 columns: id, entity, sentiment, text
    df = spark.read.csv(
        data_path,
        header=False,
        inferSchema=True
    ).toDF("id", "entity", "sentiment", "text")

    # Handling nulls immediately after load
    # Matches the pipeline expectation: Rename 'sentiment' to 'target', 'text' to 'cleaned_text'
    df = df.withColumnRenamed("sentiment", "target") \
           .withColumnRenamed("text", "cleaned_text") \
           .dropna(subset=["cleaned_text", "target"])

    # Merge 'Irrelevant' into 'Neutral'
    from pyspark.sql.functions import when
    df = df.withColumn("target", when(
        col("target") == "Irrelevant", "Neutral").otherwise(col("target")))

    # Remove URLs, mentions, and non-alphanumeric characters
    df = df.withColumn("cleaned_text", lower(col("cleaned_text")))
    df = df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"http\S+", ""))
    df = df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"@\w+", ""))
    df = df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"[^a-zA-Z\s]", ""))
    df = df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"\s+", " "))

    # Load Validation Data
    val_df = spark.read.csv(
        validation_path,
        header=False,
        inferSchema=True
    ).toDF("id", "entity", "sentiment", "text")

    val_df = val_df.withColumnRenamed("sentiment", "target") \
        .withColumnRenamed("text", "cleaned_text") \
        .dropna(subset=["cleaned_text", "target"])

    # Merge 'Irrelevant' into 'Neutral' for validation set too
    val_df = val_df.withColumn("target", when(
        col("target") == "Irrelevant", "Neutral").otherwise(col("target")))

    # Apply same cleaning to validation set
    val_df = val_df.withColumn("cleaned_text", lower(col("cleaned_text")))
    val_df = val_df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"http\S+", ""))
    val_df = val_df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"@\w+", ""))
    val_df = val_df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"[^a-zA-Z\s]", ""))
    val_df = val_df.withColumn("cleaned_text", regexp_replace(
        col("cleaned_text"), r"\s+", " "))

    # 3. Label Preparation
    # Convert 'target' column to indexed labels
    label_indexer = StringIndexer(
        inputCol="target",
        outputCol="label_indexed",
        handleInvalid="skip"  # skip rows with unseen labels
    )

    # 4. Text Feature Pipeline (Spark-Native)
    # Stage A: Tokenization
    tokenizer = Tokenizer(
        inputCol="cleaned_text",
        outputCol="tokens"
    )

    # Stage B: Stop Words Removal
    remover = StopWordsRemover(
        inputCol="tokens",
        outputCol="filtered_tokens"
    )

    # Stage C: Count Vectorizer (Term Frequency)
    vectorizer = CountVectorizer(
        inputCol="filtered_tokens",
        outputCol="raw_features",
        vocabSize=5000,
        minDF=5
    )

    # Stage D: IDF (Inverse Document Frequency)
    idf = IDF(
        inputCol="raw_features",
        outputCol="features"
    )

    # 5. Logistic Regression (Distributed Training)
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="label_indexed",
        maxIter=20,
        regParam=0.01,  # Added some regularization
        elasticNetParam=0.0  # L2 penalty
    )

    # 6. Pipeline Construction
    # Fit label indexer separately to get labels
    label_model = label_indexer.fit(df)
    df = label_model.transform(df)

    # Also transform the validation set so it has 'label_indexed'
    val_df = label_model.transform(val_df)

    label_converter = IndexToString(
        inputCol="prediction",
        outputCol="predicted_label",
        labels=label_model.labels
    )

    pipeline = Pipeline(stages=[
        tokenizer,
        remover,
        vectorizer,
        idf,
        lr,
        label_converter
    ])

    # 7. Train / Test Split
    print("Using separate validation file for testing...")
    train_df = df  # Use all of training data
    test_df = val_df  # Use validation file for evaluation

    # Fit the pipeline
    print("Training model...")
    model = pipeline.fit(train_df)
    print("Model training complete.")

    # 8. Evaluation
    print("Evaluating model...")
    predictions = model.transform(test_df)

    evaluator = MulticlassClassificationEvaluator(
        labelCol="label_indexed",
        predictionCol="prediction",
        metricName="accuracy"
    )

    accuracy = evaluator.evaluate(predictions)
    print(f"Test Accuracy: {accuracy:.4f}")

    # Also print other metrics for completeness
    f1_score = evaluator.setMetricName("f1").evaluate(predictions)
    print(f"Test F1 Score: {f1_score:.4f}")

    # 9. Save the Spark ML Model
    print(f"Saving model to file:///opt/spark/work-dir/spark_sentiment_model ...")
    model.write().overwrite().save("file:///opt/spark/work-dir/spark_sentiment_model")
    print("Model saved successfully.")

    # 10. Stop Spark Cleanly
    spark.stop()


if __name__ == "__main__":
    main()
