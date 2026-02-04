package com.sentiments.core.services;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class TweetConsumer {

    @KafkaListener(topics = "tweets.raw", groupId = "spring-consumer-group")
    public void listen(String message) {
        System.out.println("Received tweet: " + message);
    }
}
