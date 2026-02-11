#!/bin/bash

API_URL="http://localhost:8090/api/tweets"
HEADER="Content-Type: application/json"

echo "Sending test tweets to $API_URL..."

# Negative Tweets
echo "Sending Negative Tweets..."
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I absolutely hate this product, it is very bad!", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Worst experience ever. Do not recommend.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Broken upon arrival. Terrible quality control.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Customer service was rude and unhelpful.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I regret buying this garbage.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Waste of money. Complete failure.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Disappointed with the delay and shipping.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "The app crashes all the time. Unusable so buggy.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Terrible software updates making things worse.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I am furious about this billing error.", "source": "curl-test"}'
echo ""

# Positive Tweets
echo "Sending Positive Tweets..."
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I absolutely love this product, it is amazing!", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Best experience ever. Highly recommend.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Works perfectly out of the box. Great quality.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Customer service was polite and very helpful.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I am so happy with this purchase.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Worth every penny. Complete success.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Impressed with the speed of shipping.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "The app runs smoothly. Very intuitive interface.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Wonderful software updates bringing cool features.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I am delighted with the support team.", "source": "curl-test"}'
echo ""

# Neutral Tweets
echo "Sending Neutral Tweets..."
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I bought this product yesterday.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "The delivery arrived at 5 PM.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "It is what it is.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "I have a question about the specifications.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Using this for the first time.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Waiting for the next update.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Just checking the features.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Comparing this with another brand.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Reading the manual right now.", "source": "curl-test"}'
echo ""
curl -X POST "$API_URL" -H "$HEADER" -d '{"text": "Installation completed.", "source": "curl-test"}'
echo ""

echo "Done sending 30 test tweets."
