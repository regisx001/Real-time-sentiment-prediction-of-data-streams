package com.sentiments.core.services;

import java.time.ZoneOffset;
import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.sentiments.core.domain.dto.TweetEvent;
import com.sentiments.core.domain.entities.RawTweet;
import com.sentiments.core.repository.RawTweetRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TweetService {

    private final RawTweetRepository rawTweetRepository;
    private final TweetProducer tweetProducer;

    @Transactional
    public RawTweet createTweet(String text, String source) {
        // 1. Save to DB
        RawTweet tweet = new RawTweet(text, source);
        tweet = rawTweetRepository.save(tweet);

        // 2. Produce event to Kafka
        TweetEvent event = new TweetEvent(
                tweet.getId().toString(),
                tweet.getText(),
                tweet.getIngestedAt().toEpochSecond(ZoneOffset.UTC));
        tweetProducer.sendTweet(event);

        return tweet;
    }

    public List<RawTweet> getAllTweets() {
        return rawTweetRepository.findAll();
    }
}
