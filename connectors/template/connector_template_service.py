#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("NEW_SERVICE_API_URL")
API_KEY = os.getenv("NEW_SERVICE_API_KEY")
USERNAME = os.getenv("NEW_SERVICE_USERNAME")
PASSWORD = os.getenv("NEW_SERVICE_PASSWORD")

def send_message(message: str, options: dict):
    """
    Send a message to the new service.

    Args:
        message (str): The message to send.
        options (dict): Additional options for the message.

    Returns:
        Response object: The response from the service.
    """
    url = f"{API_URL}/send/message"
    auth = (USERNAME, PASSWORD)
    data = {'message': message}
    response = requests.post(url, headers={'Authorization': f'Bearer {API_KEY}'}, data=data, auth=auth)
    return response

