package com.sentiments.core.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaTopicsConfig {
    @Bean
    public NewTopic rawTweetsTopic() {
        return TopicBuilder.name("tweets.raw")
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic processedTweetsTopic() {
        return TopicBuilder.name("tweets.processed")
                .partitions(3)
                .replicas(1)
                .build();
    }
}
