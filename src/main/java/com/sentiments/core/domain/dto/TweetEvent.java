package com.sentiments.core.domain.dto;

public record TweetEvent(
        String tweetId,
        String text,
        long timestamp) {
}
