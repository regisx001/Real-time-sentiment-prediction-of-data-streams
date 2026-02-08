# Machine Learning Notebooks

This directory contains the complete offline machine learning pipeline for training a sentiment classification model.

## Overview

The workflow is divided into four main steps (Phase A):

1. **Data Loading & Validation (A1)**: Load cleaned dataset, validate columns, handle null/empty values, inspect label distribution.
2. **Feature Extraction (A2)**: Convert text to numerical features using TF-IDF vectorization.
3. **Model Training & Evaluation (A3)**: Train Logistic Regression classifier and evaluate performance.
4. **Model Persistence (A4)**: Save the complete inference pipeline (vectorizer + classifier) for streaming.

## Notebooks

### 01-Data-Exploration.ipynb
*Located in `ml/explore.ipynb`*

Explores the raw tweet dataset and performs initial preprocessing:
- Loads the dataset with proper column naming.
- Displays dataset shape and sample records.
- Maps sentiment labels for readability (0=Negative, 2=Neutral, 4=Positive).
- Removes unnecessary columns (ids, date, flag, user).
- Analyzes text length distribution by sentiment.
- Cleans text: removes URLs, mentions, hashtags.
- Exports cleaned data to `data/cleaned.csv`.

### 02-Model-Training.ipynb

Builds and trains the sentiment classification model:

**Step A1 - Data Loading & Validation**
- Loads cleaned dataset from `data/cleaned.csv`.
- Validates presence of `cleaned_text` and `target` columns.
- Removes null and empty text entries.
- Checks label distribution (3-class problem: Negative, Neutral, Positive).
- Defines training variables: `X_text` and `y`.

**Step A2 - Feature Extraction with TF-IDF**
- Converts text to numerical features using `TfidfVectorizer`.
- Configuration:
  - `max_features=5000`: Limits vocabulary size.
  - `ngram_range=(1, 2)`: Captures words and bigrams.
  - `min_df=5`: Ignores words appearing in fewer than 5 documents.
  - `stop_words='english'`: Removes common English words.
- Output: `X_features` (sparse matrix) and trained `vectorizer` object.

**Step A3 - Train & Evaluate Model**
- Splits data: 80% training, 20% testing (stratified).
- Trains Logistic Regression classifier.
  - Fast to train and predict.
  - Interpretable (coefficients show word importance).
  - Strong baseline for text classification.
- Evaluates on test set:
  - Accuracy
  - Precision, Recall, F1-Score (per class)
  - Top 10 words driving positive and negative sentiment.
- Metrics saved to `ml/metrics.txt`.

**Step A4 - Persist Pipeline**
- Bundles `vectorizer` and `classifier` into a single dictionary.
- Serializes to `ml/sentiment_model.pkl` using joblib.
- This file is loaded by the Spark streaming job for real-time inference.

## Artifacts

After running the notebooks, the following artifacts are generated:

- `data/cleaned.csv`: Cleaned tweet dataset (target, cleaned_text).
- `ml/sentiment_model.pkl`: Serialized inference pipeline (vectorizer + classifier).
- `ml/metrics.txt`: Model performance metrics on test set.

## Running the Notebooks

1. Ensure the conda environment is activated or dependencies are installed:
   ```bash
   pip install pandas scikit-learn numpy joblib
   ```

2. Run notebooks in order:
   - First: `ml/explore.ipynb` (generates `data/cleaned.csv`).
   - Second: `02-Model-training.ipynb` (generates `ml/sentiment_model.pkl` and `ml/metrics.txt`).

3. Verify outputs exist before running the Spark streaming job.

## Key Design Decisions

- **TF-IDF over embeddings**: Simple, fast, interpretable, and sufficient for this task.
- **Logistic Regression over deep learning**: Lower latency, lower resource footprint, fully explainable.
- **No class balancing**: We acknowledge imbalance but keep the pipeline clean; focus is on the baseline.
- **80/20 train/test split**: Standard practice; large enough test set for reliable metrics.

## Integration with Streaming

The `sentiment_model.pkl` is the bridge between offline training and online inference:

1. Spark loads the model at startup.
2. For each incoming tweet, the vectorizer transforms the text.
3. The classifier predicts the sentiment.
4. Result is written to PostgreSQL or output topic.

This ensures consistency: the same feature extraction and model are used offline and online.
