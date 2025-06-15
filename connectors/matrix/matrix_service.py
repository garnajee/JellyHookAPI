#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv
import logging

#logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')

load_dotenv()

MATRIX_URL = os.getenv("MATRIX_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ROOM_ID = os.getenv("ROOM_ID")

def format_message(message: dict) -> str:
    """
    Format message for Matrix channel.

    Args:
        message (dict): Message to send.

    Returns:
        str: Formatted message for Matrix.
    """

    try:
        trailers = message.get("trailer",[])
        if trailers is None:
            trailers = []
        if len(trailers) == 1:
            trailer_text = f"\n[Trailer]({trailers[0]})"
        elif len(trailers) == 2:
            trailer_text = f"\n[Trailer FR]({trailers[0]})\n[Trailer EN]({trailers[1]})"
        else:
            trailer_text = ""

        links = message.get("media_link", {})
        if links is None:
            links = {}
        link_text = ""
        if "imdb" in links:
            link_text += f"\n[IMDb]({links['imdb']})"
        if "tmdb" in links:
            link_text += f"\n[TMDb]({links['tmdb']})"

        formatted_message = f"#{message.get('title')}\n"
        if message.get('description'):
            formatted_message += f"```{message.get('description')}```\n"
        formatted_message += link_text
        formatted_message += trailer_text
        return formatted_message
    except Exception as e:
        logging.error(f"Error formatting message: {e}")
        return ""

def html_format_message(message: dict) -> str:
    """
    Format message for Matrix channel in HTML.

    Args:
        message (dict): Message to send.

    Returns:
        str: Formatted message for Matrix in HTML.
    """
    try:
        trailers = message.get("trailer", [])
        if len(trailers) == 1:
            trailer_text = f'<br><a href="{trailers[0]}">Trailer</a>'
        elif len(trailers) == 2:
            trailer_text = f'<br><a href="{trailers[0]}">Trailer FR</a><br><a href="{trailers[1]}">Trailer EN</a>'
        else:
            trailer_text = ""

        links = message.get("media_link", {})
        link_text = ""
        if "imdb" in links:
            link_text += f'<br><br><a href="{links["imdb"]}">IMDb</a>'
        if "tmdb" in links:
            link_text += f'<br><a href="{links["tmdb"]}">TMDb</a>'

        formatted_message = f'<h1>{message.get("title")}</h1><br/>'
        if message.get('description'):
            formatted_message += f'<pre>{message.get("description")}</pre>'
        formatted_message += link_text
        formatted_message += trailer_text
        return formatted_message
    except Exception as e:
        logging.error(f"Error formatting message: {e}")
        return ""

def upload_image(image_path: str) -> str:
    """
    Upload image to the Matrix server.

    Args:
        image_path (str): The local path to the image.

    Returns:
        str: The content URI of the uploaded image.
    """
    try:
        url = f"{MATRIX_URL}/_matrix/media/r0/upload?filename={os.path.basename(image_path)}"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "image/jpeg"
        }
        with open(image_path, 'rb') as image_file:
            response = requests.post(url, headers=headers, data=image_file)
        return response.json().get("content_uri")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error uploading image: {e}")
        return ""

def send_message(message: dict, options: dict = None) -> requests.Response:
    """
    Send a message to a Matrix room.

    Args:
        message (dict): The message to send.
        options (dict): Additional options for the message, including image path.

    Returns:
        Response object: The response from the Matrix server.
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        formatted_message = format_message(message)
        html_formatted_message = html_format_message(message)

        # Check if we need to send the image
        send_image = options.get('send_image')
        image_path = options.get('picture_path')
        if send_image:
            if not image_path:
                logging.error("image_path is None")
                raise ValueError("image_path is None")
        
            # Upload the image and get the content URI
            image_uri = upload_image(image_path)
            if not image_uri:
                logging.error("Failed to upload image")
                raise Exception("Failed to upload image")

            # Send the image message
            send_image_url = f"{MATRIX_URL}/_matrix/client/r0/rooms/{ROOM_ID}/send/m.room.message"
            image_info = {
                "msgtype": "m.image",
                "body": os.path.basename(image_path),
                "url": image_uri,
                "info": {
                    "mimetype": "image/jpeg",
                    "size": os.path.getsize(image_path),
                    "w": 342,
                    "h": 513
                }
            }

            response = requests.post(send_image_url, headers=headers, json=image_info)
            response.raise_for_status()

        # Send the formatted message
        send_text_url = f"{MATRIX_URL}/_matrix/client/r0/rooms/{ROOM_ID}/send/m.room.message"
        # associated documentation: https://spec.matrix.org/latest/client-server-api/#send-m-room-message
        # change to m.text and commend format and formatted_body if you encounter issue sending message.
        text_info = {
            "msgtype": "m.notice", # for automated client, no answer expected
            "body": formatted_message, # notice text to send. Plain text, if html client formatting is not supported
            "format": "org.matrix.custom.html", # format used in formatted_body
            "formatted_body": html_formatted_message # formatted version of body. Required if format is specified
        }
        response = requests.post(send_text_url, headers=headers, json=text_info)
        response.raise_for_status()

        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message: {e}")
        return None

if __name__ == "__main__":
    message = {
        "title": "Example Title",
        "description": "Example Description",
        "trailer": ["http://example.com/trailer1", "http://example.com/trailer2"],
        "media_link": {
            "imdb": "http://example.com/imdb",
            "tmdb": "http://example.com/tmdb"
        }
    }
    options = {
        "send_image": True,
        "picture_path": "https://image.tmdb.org/t/p/w342/t1i10ptOivG4hV7erkX3tmKpiqm.jpg"
    }
    response = send_message(message, options)
    if response:
        logging.info("Response:", response.status_code)
    else:
        logging.info("Failed to send message")

