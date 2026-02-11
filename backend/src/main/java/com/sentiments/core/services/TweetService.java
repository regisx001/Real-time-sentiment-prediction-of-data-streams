package com.sentiments.core.services;

import com.sentiments.core.domain.dto.TweetEvent;
import com.sentiments.core.domain.entities.Tweet;
import com.sentiments.core.repository.TweetRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.ZoneOffset;
import java.util.List;

@Service
public class TweetService {

    private final TweetRepository tweetRepository;
    private final TweetProducer tweetProducer;

    public TweetService(TweetRepository tweetRepository, TweetProducer tweetProducer) {
        this.tweetRepository = tweetRepository;
        this.tweetProducer = tweetProducer;
    }

    @Transactional
    public Tweet createTweet(String text, String source) {
        // 1. Save to DB
        Tweet tweet = new Tweet(text, source);
        tweet = tweetRepository.save(tweet);

        // 2. Produce event to Kafka
        TweetEvent event = new TweetEvent(
                tweet.getId().toString(),
                tweet.getText(),
                tweet.getIngestedAt().toEpochSecond(ZoneOffset.UTC)
        );
        tweetProducer.sendTweet(event);

        return tweet;
    }

    public List<Tweet> getAllTweets() {
        return tweetRepository.findAll();
    }
}
