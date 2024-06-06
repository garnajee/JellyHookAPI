#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
WHATSAPP_API_USERNAME = os.getenv("WHATSAPP_API_USERNAME")
WHATSAPP_API_PWD = os.getenv("WHATSAPP_API_PWD")

def send_message(message: str, options: dict = {}) -> requests.Response:
    send_image = options.get('send_image', False)
    picture_path = options.get('picture_path', None)

    url = f"{WHATSAPP_API_URL}/send/image" if send_image else f"{WHATSAPP_API_URL}/send/message"
    auth = (WHATSAPP_API_USERNAME, WHATSAPP_API_PWD)
    headers = {'accept': 'application/json'}
    data = {'phone': WHATSAPP_NUMBER}

    try:
        if send_image and picture_path:
            data['caption'] = message
            data['compress'] = "True"
            files = {'image': ('image', open(picture_path, 'rb'), 'image/png')}
            response = requests.post(url, headers=headers, data=data, auth=auth, files=files)
        else:
            data['message'] = message
            response = requests.post(url, headers=headers, data=data, auth=auth)

        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"Error sending WhatsApp message: {e}")
        return None


if __name__ == "__main__":
    message = "Test message"
    send_image = False
    print(send_whatsapp_message(message, send_image))
    if send_image:
        picture_path = "path/to/your/image.png"
        print(send_whatsapp_message(message, send_image, picture_path))

