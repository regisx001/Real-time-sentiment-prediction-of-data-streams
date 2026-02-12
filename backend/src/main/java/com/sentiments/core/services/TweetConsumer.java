package com.sentiments.core.services;

import java.util.Optional;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.sentiments.core.domain.dto.ProcessedTweetEvent;
import com.sentiments.core.domain.entities.RawTweet;
import com.sentiments.core.repository.RawTweetRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
public class TweetConsumer {

    private final RawTweetRepository rawTweetRepository;

    @KafkaListener(topics = "tweets.processed", groupId = "core-consumer")
    @Transactional
    public void consume(ProcessedTweetEvent event) {
        log.info("Consumed processed tweet: " + event);
        try {
            Long id = Long.valueOf(event.tweetId());
            Optional<RawTweet> tweetOpt = rawTweetRepository.findById(id);
            if (tweetOpt.isPresent()) {
                RawTweet tweet = tweetOpt.get();
                tweet.setSentiment(mapSentiment(event.sentiment()));
                tweet.setScore(event.score());
                rawTweetRepository.save(tweet);
            } else {
                log.error("Tweet not found with ID: " + id);
            }
        } catch (NumberFormatException e) {
            log.error("Invalid tweet ID format: " + event.tweetId());

        }
    }

    private String mapSentiment(String rawSentiment) {
        if (rawSentiment == null) {
            return "UNKNOWN";
        }
        String normalized = rawSentiment.trim();
        return switch (normalized) {
            case "Positive", "positive" -> "POSITIVE";
            case "Negative", "negative" -> "NEGATIVE";
            case "Neutral", "neutral" -> "NEUTRAL";
            case "Irrelevant", "irrelevant" -> "NEUTRAL"; // Just in case model hasn't been retrained yet
            default -> normalized.toUpperCase();
        };
    }
}
