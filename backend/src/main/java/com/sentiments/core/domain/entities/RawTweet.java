package com.sentiments.core.domain.entities;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "raw_tweets")
@Setter
@Getter
public class RawTweet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "tweet_text", nullable = false)
    private String text;

    @Column(name = "source")
    private String source;

    @Column(name = "sentiment")
    private String sentiment;

    @Column(name = "score")
    private double score;

    @Column(name = "ingested_at", nullable = false)
    private LocalDateTime ingestedAt;

    public RawTweet() {
    }

    public RawTweet(String text, String source) {
        this.text = text;
        this.source = source;
        this.ingestedAt = LocalDateTime.now();
    }

}
