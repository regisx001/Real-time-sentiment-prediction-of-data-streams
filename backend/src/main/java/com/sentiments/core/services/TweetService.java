package com.sentiments.core.services;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.sentiments.core.domain.dto.TweetEvent;
import com.sentiments.core.domain.entities.Tweet;
import com.sentiments.core.repository.TweetRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TweetService {

    private final TweetRepository rawTweetRepository;
    private final TweetProducer tweetProducer;

    @Transactional
    public Tweet createTweet(String text, String source) {
        // 1. Save to DB
        Tweet tweet = new Tweet();
        tweet.setIngestedAt(LocalDateTime.now());

        Map<String, Object> rawData = new HashMap<>();
        rawData.put("text", text);
        rawData.put("source", source);
        tweet.setRawData(rawData);

        tweet = rawTweetRepository.save(tweet);

        // 2. Produce event to Kafka
        TweetEvent event = new TweetEvent(
                tweet.getId().toString(),
                (String) tweet.getRawData().get("text"),
                tweet.getIngestedAt().toEpochSecond(ZoneOffset.UTC));
        tweetProducer.sendTweet(event);

        return tweet;
    }

    public List<Tweet> getAllTweets() {
        return rawTweetRepository.findAll();
    }
}
