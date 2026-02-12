package com.sentiments.core.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.sentiments.core.domain.entities.RawTweet;

@Repository
public interface RawTweetRepository extends JpaRepository<RawTweet, Long> {
}
