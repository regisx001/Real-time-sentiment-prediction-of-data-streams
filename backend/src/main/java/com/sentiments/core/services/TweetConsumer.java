package com.sentiments.core.services;

import java.util.Optional;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.sentiments.core.domain.dto.ProcessedTweetEvent;
import com.sentiments.core.domain.entities.Tweet;
import com.sentiments.core.repository.TweetRepository;

@Service
public class TweetConsumer {

    private final TweetRepository tweetRepository;

    public TweetConsumer(TweetRepository tweetRepository) {
        this.tweetRepository = tweetRepository;
    }

    @KafkaListener(topics = "processed-tweets", groupId = "core-consumer")
    @Transactional
    public void consume(ProcessedTweetEvent event) {
        System.out.println("Consumed processed tweet: " + event);
        try {
            Long id = Long.parseLong(event.tweetId());
            Optional<Tweet> tweetOpt = tweetRepository.findById(id);
            if (tweetOpt.isPresent()) {
                Tweet tweet = tweetOpt.get();
                tweet.setSentiment(mapSentiment(event.sentiment()));
                tweet.setScore(event.score());
                tweetRepository.save(tweet);
            } else {
                System.err.println("Tweet not found with ID: " + id);
            }
        } catch (NumberFormatException e) {
            System.err.println("Invalid tweet ID format: " + event.tweetId());
        }
    }

    private String mapSentiment(String rawSentiment) {
        if (rawSentiment == null) {
            return "UNKNOWN";
        }
        // Handle numeric sentiment from Sentiment140 dataset style (0=Negative,
        // 4=Positive)
        // Also keep support for explicit strings if sent by other producers
        String normalized = rawSentiment.trim();
        return switch (normalized) {
            case "4", "4.0" -> "POSITIVE";
            case "0", "0.0" -> "NEGATIVE";
            case "2", "2.0" -> "NEUTRAL";
            // Handle text-based labels from Twitter Training dataset
            case "Positive", "positive" -> "POSITIVE";
            case "Negative", "negative" -> "NEGATIVE";
            case "Neutral", "neutral" -> "NEUTRAL";
            case "Irrelevant", "irrelevant" -> "NEUTRAL"; // Just in case model hasn't been retrained yet
            default -> normalized.toUpperCase();
        };
    }
}
