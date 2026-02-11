package com.sentiments.core.domain.dto;

public record ProcessedTweetEvent(
        String tweetId,
        String sentiment,
        double score) {
}
