package com.sentiments.core.services;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class TweetProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;

    public TweetProducer(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendTweet(String tweet) {
        kafkaTemplate.send("tweets.raw", tweet);
    }
}
