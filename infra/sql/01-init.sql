CREATE TABLE IF NOT EXISTS raw_tweets (
    id BIGSERIAL PRIMARY KEY,
    tweet_text TEXT NOT NULL,
    source VARCHAR(50) DEFAULT 'kafka',
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optional but recommended index
CREATE INDEX IF NOT EXISTS idx_raw_tweets_ingested_at
ON raw_tweets (ingested_at);
