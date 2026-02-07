package com.sentiments.core.services;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

import com.sentiments.core.domain.dto.TweetEvent;

@Service
public class TweetConsumer {

    @KafkaListener(topics = "tweets.raw", groupId = "debug-consumer")
    public void consume(TweetEvent tweet) {
        System.out.println("Consumed tweet: " + tweet);
    }
}
