package com.sentiments.core.controllers;

import com.sentiments.core.domain.entities.Tweet;
import com.sentiments.core.services.TweetService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/tweets")
public class TweetController {

    private final TweetService tweetService;

    public TweetController(TweetService tweetService) {
        this.tweetService = tweetService;
    }

    @PostMapping
    public ResponseEntity<Tweet> createTweet(@RequestBody Map<String, String> payload) {
        String text = payload.get("text");
        String source = payload.getOrDefault("source", "api");
        if (text == null || text.isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        Tweet created = tweetService.createTweet(text, source);
        return ResponseEntity.ok(created);
    }

    @GetMapping
    public ResponseEntity<List<Tweet>> listTweets() {
        return ResponseEntity.ok(tweetService.getAllTweets());
    }
}
