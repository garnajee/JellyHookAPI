#!/usr/bin/env python3

import os
import importlib
import logging
from flask import Flask, request, jsonify
from utils.processing import handle_media, send_to_all_connectors

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONNECTORS_DIR = 'connectors'

def load_connectors():
    connectors = {}
    for root, dirs, files in os.walk(CONNECTORS_DIR):
        for file in files:
            if file.endswith('_service.py'):
                connector_name = root.split(os.sep)[-1]
                module_name = f"{CONNECTORS_DIR}.{connector_name}.{file[:-3]}"
                module = importlib.import_module(module_name)
                connectors[connector_name] = module
    return connectors

connectors = load_connectors()

@app.route('/api', methods=['POST'])
def receive_data():
    if not request.is_json:
        return jsonify({'message': 'Data is not json!'}), 400

    data = request.json
    media_type = data.get('media_type', '')
    title = data.get('title', '')
    imdb = data.get('imdb', '')
    tmdb = data.get('tmdb', None)

    try:
        tmdb = int(tmdb) if tmdb else None
    except ValueError:
        return jsonify({'message': 'Invalid TMDB ID!'}), 400

    try:
        if media_type and title:
            message, send_image, picture_path = handle_media(media_type, title, imdb, tmdb)
            send_to_all_connectors(connectors, message, send_image, picture_path)
            return jsonify({'message': 'Data received successfully!'})
        else:
            return jsonify({'message': 'Missing media_type or title!'}), 400
    except Exception as e:
        logging.error(f"Error handling media: {e}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7778)

