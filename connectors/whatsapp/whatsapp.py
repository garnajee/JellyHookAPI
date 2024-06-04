#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
WHATSAPP_API_USERNAME = os.getenv("WHATSAPP_API_USERNAME")
WHATSAPP_API_PWD = os.getenv("WHATSAPP_API_PWD")

def send_whatsapp_message(message: str, send_image: bool = False, picture_path: str = None) -> requests.Response:
    """
    Send a message to WhatsApp API.

    Args:
        message (str): Message to be sent.
        send_image (bool, optional): Whether to send an image. Defaults to False.
        picture_path (str, optional): Path to the image file. Defaults to None.

    Returns:
        requests.Response: Response from the WhatsApp API.
    """
    url = f"{WHATSAPP_API_URL}/send/image" if send_image else f"{WHATSAPP_API_URL}/send/message"
    auth = (WHATSAPP_API_USERNAME, WHATSAPP_API_PWD)
    headers = {'accept': 'application/json'}
    data = {'phone': WHATSAPP_NUMBER}
    if send_image:
        data['caption'] = message
        data['compress'] = "True"
        files = {'image': ('image', open(picture_path, 'rb'), 'image/png')}
        response = requests.post(url, headers=headers, data=data, auth=auth, files=files)
    else:
        data['message'] = message
        response = requests.post(url, headers=headers, data=data, auth=auth)
    return response

if __name__ == "__main__":
    message = "Test message"
    send_image = False
    print(send_whatsapp_message(message, send_image))
    if send_image:
        picture_path = "path/to/your/image.png"
        print(send_whatsapp_message(message, send_image, picture_path))

