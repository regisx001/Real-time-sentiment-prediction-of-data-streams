package com.sentiments.core.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sentiments.core.domain.dto.TweetEvent;
import com.sentiments.core.services.TweetProducer;

@RestController
@RequestMapping("/api/kafka")
public class KafkaController {

    private final TweetProducer tweetProducer;

    public KafkaController(TweetProducer tweetProducer) {
        this.tweetProducer = tweetProducer;
    }

    @PostMapping("/send")
    public ResponseEntity<String> sendTweet(@RequestBody TweetEvent tweet) {
        tweetProducer.sendTweet(tweet);
        return ResponseEntity.ok("Message sent to Kafka");
    }
}
