#!/usr/bin/env python3

import os
import json
from flask import Flask, jsonify, abort

app = Flask(__name__)

DATA_DIR = 'data'

@app.route('/Users/<user_id>/Items/<item_id>', methods=['GET'])
def get_item_details(user_id, item_id):
    """
    Simulates the Jellyfin API endpoint for fetching item details.
    It looks for a JSON file corresponding to the item_id.
    """
    # We create a mapping to find the correct file
    # In a real mock, you could have more complex logic
    file_map = {
        "movie123": "movie_details.json",
        "episode456": "episode_details.json",
        "docu101": "documentary_details.json"
    }

    filename = file_map.get(item_id)
    if not filename:
        # If the item_id is not in our map (e.g., for a season),
        # return a 404 Not Found, which your code should handle gracefully.
        print(f"Mock server received request for unknown item_id: {item_id}")
        abort(404, description=f"Item {item_id} not found")

    filepath = os.path.join(DATA_DIR, filename)

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"Mock server returning data for item_id: {item_id} from {filename}")
        return jsonify(data)
    except FileNotFoundError:
        print(f"Mock server could not find file: {filepath}")
        abort(404, description=f"Details file for {item_id} not found")

if __name__ == '__main__':
    # We run on port 8096 to mimic the real Jellyfin server port inside Docker
    app.run(host='0.0.0.0', port=8096, debug=True)

