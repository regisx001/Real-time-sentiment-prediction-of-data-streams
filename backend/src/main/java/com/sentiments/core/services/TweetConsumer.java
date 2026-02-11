package com.sentiments.core.services;

import com.sentiments.core.domain.dto.ProcessedTweetEvent;
import com.sentiments.core.domain.entities.Tweet;
import com.sentiments.core.repository.TweetRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

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
                tweet.setSentiment(event.sentiment());
                tweetRepository.save(tweet);
            } else {
                System.err.println("Tweet not found with ID: " + id);
            }
        } catch (NumberFormatException e) {
            System.err.println("Invalid tweet ID format: " + event.tweetId());
        }
    }
}
