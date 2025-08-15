#!/usr/bin/env bash

echo "--- Sending Movie Added Notification ---"
curl -X POST -H "Content-Type: application/json" --data @- http://localhost:7778/api <<EOF
{
  "media_type": "movie",
  "title": "Inception (2010) has been added",
  "imdb": "tt1375666",
  "tmdb": "27205",
  "item_id": "movie123",
  "watch_link": "http://example.com/watch/movie123"
}
EOF
echo "\n--- Done ---\n"

