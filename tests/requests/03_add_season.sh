#!/usr/bin/env bash

echo "--- Sending Season Added Notification ---"
curl -X POST -H "Content-Type: application/json" --data @- http://localhost:7778/api <<EOF
{
  "media_type": "tv",
  "title": "Season-added: The Office, Season 2",
  "imdb": "tt0386676",
  "tmdb": "2316",
  "item_id": "season789",
  "watch_link": "http://example.com/watch/season789"
}
EOF
echo "\n--- Done ---\n"

