#!/bin/bash

# Script to open the PostgreSQL console
# This connects to the 'sentiments' container running TimescaleDB

echo "Opening PSQL Console for database 'realtime_sentiments_analysis'..."
echo "Use \q to exit."
echo "---------------------------------------------------"

# Run psql inside the 'sentiments' container
sudo docker exec -it sentiments psql -U admin -d realtime_sentiments_analysis

echo ""
echo "PSQL session closed."
