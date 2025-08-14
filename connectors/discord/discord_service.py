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

    links = message.get("media_link", {})
    link_text = ""
    if "imdb" in links:
        link_text += f"\n\n[IMDb]({links['imdb']})"
    if "tmdb" in links:
        link_text += f"\n[TMDb]({links['tmdb']})"

    embed = {
        "title": message.get("title", "Notification"),
        "description": message.get("description","")+link_text+trailer_text,
        "color": 3447003,  # light blue
        "fields": [],
        "footer": {
            "text": datetime.now().strftime("%H:%M - %d/%m/%Y")
        }
    }

    technical_details = message.get("technical_details")
    if technical_details:
        details_text = ""
        if 'video' in technical_details:
            video = technical_details['video']
            details_text += f"**Video:** {video.get('resolution', 'N/A')} | {video.get('codec', 'N/A')} | {video.get('hdr', 'N/A')}\n"

        if 'audio' in technical_details:
            audio_tracks = " | ".join(technical_details['audio'])
            details_text += f"**Audio:** {audio_tracks}\n"

        if 'subtitles' in technical_details and technical_details['subtitles']:
            subtitle_tracks = " | ".join(technical_details['subtitles'])
            details_text += f"**Subtitles:** {subtitle_tracks}"

        if details_text:
            embed["fields"].append({
                "name": "Technical Details",
                "value": details_text.strip(),
                "inline": False
            })

    data = {
        "content": "",
        "embeds": [embed]
    }

    if options.get('send_image') and options.get('picture_path'):
        data["embeds"][0]["image"] = {"url": f"attachment://{os.path.basename(options['picture_path'])}"}

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

