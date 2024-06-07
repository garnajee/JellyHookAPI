#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("NEW_SERVICE_API_URL")
API_KEY = os.getenv("NEW_SERVICE_API_KEY")
USERNAME = os.getenv("NEW_SERVICE_USERNAME")
PASSWORD = os.getenv("NEW_SERVICE_PASSWORD")

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
    Send a message to the new service.

    Args:
        message (dict): The message to send.
        options (dict): Additional options for the message.

    Returns:
        Response object: The response from the service.
    """

    formatted_message = format_message(message)

    url = f"{API_URL}/send/message"
    auth = (USERNAME, PASSWORD)
    data = {'message': formatted_message}

    try:
        response = requests.post(url, headers={'Authorization': f'Bearer {API_KEY}'}, data=data, auth=auth)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return None

    return response

