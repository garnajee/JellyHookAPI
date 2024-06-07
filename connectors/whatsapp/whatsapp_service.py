#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
WHATSAPP_API_USERNAME = os.getenv("WHATSAPP_API_USERNAME")
WHATSAPP_API_PWD = os.getenv("WHATSAPP_API_PWD")

def format_message(message: dict) -> str:
    """
    Format message for WhatsApp

    Args:
        message (dict): Message to send.

    Returns:
        str: Formatted message for WhatsApp.
    """
    formatted_message = f"*{message.get('title')}*\n"
    if message.get('description'):
        formatted_message += f"```{message.get('description')}```\n"
    if message.get('media_link'):
        formatted_message += f"{message.get('media_link')}\n"
    if message.get('trailer'):
        formatted_message += message.get('trailer')
    return formatted_message

def send_message(message: dict, options: dict = None) -> requests.Response:
    """
    Send a message to WhatsApp API.

    Args:
        message (dict): Message to send.
        options (dict, optional): Options specific to the API

    Returns:
        requests.Response: Response from the WhatsApp API.
    """
    send_image = options.get('send_image', False)
    picture_path = options.get('picture_path', None)

    url = f"{WHATSAPP_API_URL}/send/image" if options and send_image else f"{WHATSAPP_API_URL}/send/message"
    auth = (WHATSAPP_API_USERNAME, WHATSAPP_API_PWD)
    headers = {'accept': 'application/json'}

    formatted_message = format_message(message)
    data = {'phone': WHATSAPP_NUMBER}

    if options and send_image and picture_path:
        data['caption'] = formatted_message
        data['compress'] = "True"
        files = {'image': ('image', open(options['picture_path'], 'rb'), 'image/png')}
    else:
        data['message'] = formatted_message
        files = None

    try:
        response = requests.post(url, headers=headers, data=data, auth=auth, files=files)
        response.raise_for_status()
        logging.info(f"Message sent successfully: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None

    return response

if __name__ == "__main__":
    message = {
        "description": "This is a test message from JellyHookAPI.",
    }
    options = {"send_image": True, "picture_path": "https://picsum.photos/200"}
    response = send_message(message, options)
    if response:
        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response content: {response.content}")

