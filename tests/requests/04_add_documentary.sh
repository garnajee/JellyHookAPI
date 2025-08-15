#!/usr/bin/env bash

echo "--- Sending Documentary Added Notification ---"
curl -X POST -H "Content-Type: application/json" --data @- http://localhost:7778/api <<EOF
{
  "media_type": "movie",
  "title": "Planet Earth II (2016) has been added",
  "imdb": "tt5491994",
  "tmdb": "67145",
  "item_id": "docu101",
  "watch_link": "http://example.com/watch/docu101"
}
EOF
echo "\n--- Done ---\n"

