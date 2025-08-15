#!/usr/bin/env bash

echo "--- Sending Episode Added Notification ---"
curl -X POST -H "Content-Type: application/json" --data @- http://localhost:7778/api <<EOF
{
  "media_type": "tv",
  "title": "Episode-added: Breaking Bad, S01E01 - Pilot",
  "imdb": "tt0959621",
  "tmdb": "62085",
  "item_id": "episode456",
  "watch_link": "http://example.com/watch/episode456"
}
EOF
echo "\n--- Done ---\n"

