package com.sentiments.core.services;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import com.sentiments.core.domain.dto.TweetEvent;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class TweetProducer {

    private final KafkaTemplate<String, TweetEvent> kafkaTemplate;
    private static final String TOPIC = "tweets";

    public TweetProducer(KafkaTemplate<String, TweetEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendTweet(TweetEvent tweet) {
        log.info("Sending tweet to Kafka: " + tweet);
        kafkaTemplate.send(TOPIC, tweet.tweetId(), tweet);
    }
}
