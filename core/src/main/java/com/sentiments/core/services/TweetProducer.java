package com.sentiments.core.services;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import com.sentiments.core.domain.dto.TweetEvent;

@Service
public class TweetProducer {

    private final KafkaTemplate<String, TweetEvent> kafkaTemplate;

    public TweetProducer(KafkaTemplate<String, TweetEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendTweet(TweetEvent tweet) {
        kafkaTemplate.send("tweets.raw", tweet);
    }
}
