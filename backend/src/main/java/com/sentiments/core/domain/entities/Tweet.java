package com.sentiments.core.domain.entities;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "raw_tweets")
public class Tweet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "tweet_text", nullable = false)
    private String text;

    @Column(name = "source")
    private String source;

    @Column(name = "sentiment")
    private String sentiment;

    @Column(name = "ingested_at", nullable = false)
    private LocalDateTime ingestedAt;

    public Tweet() {}

    public Tweet(String text, String source) {
        this.text = text;
        this.source = source;
        this.ingestedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    public String getSentiment() { return sentiment; }
    public void setSentiment(String sentiment) { this.sentiment = sentiment; }

    public LocalDateTime getIngestedAt() { return ingestedAt; }
    public void setIngestedAt(LocalDateTime ingestedAt) { this.ingestedAt = ingestedAt; }
}
