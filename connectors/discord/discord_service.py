#!/usr/bin/env python3

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def format_message_for_discord(message: dict, options: dict) -> dict:
    """
    Format the message for Discord

    Args:
        message (dict): Message to send
        options (dict, optional): Additional options for the message

    Returns:
        dict: The formatted payload for Discord.
    """

    trailers = message.get("trailer", [])
    if len(trailers) == 1:
        trailer_text = f"\n[Trailer]({trailers[0]})"
    elif len(trailers) == 2:
        trailer_text = f"\n[Trailer FR]({trailers[0]})\n[Trailer EN]({trailers[1]})"
    else:
        trailer_text = ""

    data = {
      "content": "",
      "embeds": [
        {
          "title": message.get("title", "Notification"),
          "description": message.get("description","")+"\n\n"+message.get("media_link","")+trailer_text,
          "color": 3447003,  # light blue
          "footer": {
              "text": datetime.now().strftime("%H:%M - %d/%m/%Y")
            }
        }
      ]
    }

    if options.get('send_image') and options.get('picture_path'):
        #data["embeds"][0]["thumbnail"] = {"url": f"attachment://{options['picture_path']}"}
        data["embeds"][0]["image"] = {"url": f"attachment://{os.path.basename(options['picture_path'])}"}
        #data["embeds"][0]["image"] = {"url": f"attachment://{options['picture_path']}"}

    return data

def send_message(message: dict, options: dict = None) -> requests.Response:
    """
    Send message to a Discord webhook

    Args:
        message (dict): Message to send
        options (dict, optional): Additional options for the message

    Returns:
        requests.Response: Response from the Discord API.
    """
    if not DISCORD_WEBHOOK_URL:
        logging.error("DISCORD_WEBHOOK_URL is not set in the environment variables.")
        raise ValueError("DISCORD_WEBHOOK_URL is not set in the environment variables.")

    payload = format_message_for_discord(message, options)

    try:
        files = None
        if options.get('send_image') and options.get('picture_path'):
            files = {
                'payload_json': (None, json.dumps(payload), 'application/json'),
                'file1': (open(options['picture_path'], 'rb'))
            }
            response = requests.post(DISCORD_WEBHOOK_URL, files=files)
        else:
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        response.raise_for_status()
        logging.info(f"Message sent successfully: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        logging.error(f"Response content: {response.content if response else 'No response'}")
        return None

    return response

if __name__ == "__main__":
    message = {
        "title": "Sample Title",
        "description": "This is a test description.",
        "media_link": "https://example.com",
        "trailer": "https://youtube.com/trailer"
    }
    options = {"send_image": True, "picture_path": "https://picsum.photos/200"}
    response = send_message(message, options)
    if response:
        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response content: {response.content}")

