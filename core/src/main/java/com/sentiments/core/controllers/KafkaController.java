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

    private final TweetProducer producer;

    public KafkaController(TweetProducer producer) {
        this.producer = producer;
    }

    @PostMapping("/send")
    public ResponseEntity<String> send(@RequestBody TweetEvent message) {
        producer.sendTweet(message);
        return ResponseEntity.ok("Message sent to Kafka");
    }
}
