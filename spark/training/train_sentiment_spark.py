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


def main():
    # 1. SparkSession (Driver Entry Point)
    spark = SparkSession.builder \
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
        data_path = f"file://{work_dir}/cleaned.csv"
        model_output_path = f"{work_dir}/spark_sentiment_model"
    else:
        # Fallback to local development path
        data_path = os.path.join(project_root, "data/cleaned.csv")
        model_output_path = os.path.join(
            project_root, "ml/spark_sentiment_model")

    print(f"Loading data from: {data_path}")

    # 2. Load cleaned Data (Distributed)
    # Handling nulls immediately after load
    df = spark.read.csv(
        data_path,
        header=True,
        inferSchema=True
    ).dropna(subset=["cleaned_text", "target"])

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
    pipeline = Pipeline(stages=[
        label_indexer,
        tokenizer,
        remover,
        vectorizer,
        idf,
        lr
    ])

    # 7. Train / Test Split
    print("Splitting data into training (80%) and testing (20%)...")
    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

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
    print(f"Saving model to {model_output_path}...")
    model.write().overwrite().save(model_output_path)
    print("Model saved successfully.")

    # 10. Stop Spark Cleanly
    spark.stop()


if __name__ == "__main__":
    main()
