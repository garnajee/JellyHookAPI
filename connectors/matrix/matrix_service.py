#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv
import logging
#import tempfile # Ajout pour gérer le fichier temporaire de l'image

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')

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
        if not message:
            return ""

        message_parts = []

        if message.get('title'):
            message_parts.append(f"*{message.get('title')}*")

        technical_details = message.get("technical_details")
        if technical_details:
            tech_info_parts = []

            video = technical_details.get('video', {})
            if video:
                video_str = f"🎥 {video.get('resolution', '')} | {video.get('codec', '')} | {video.get('hdr', '')}"
                tech_info_parts.append(video_str)

            audio_list = technical_details.get('audio')
            if audio_list:
                audio_str = f"🔊 {' | '.join(audio_list)}"
                tech_info_parts.append(audio_str)

            subs_list = technical_details.get('subtitles')
            if subs_list:
                subs_str = f"💬 {' | '.join(subs_list)}"
                tech_info_parts.append(subs_str)

            if tech_info_parts:
                message_parts.append(f"\n> {'  •  '.join(tech_info_parts)}")

        if message.get('description'):
            message_parts.append(f"\n```{message.get('description')}```")

        links_section = []
        links = message.get("media_link", {}) or {}
        if "imdb" in links and links["imdb"]:
            links_section.append(f"[IMDb]({links['imdb']})")
            # if your service does not support markdown link format, uncomment the next line
            #links_section.append(f"• IMDb: {links['imdb']}")
        if "tmdb" in links and links["tmdb"]:
            links_section.append(f"[TMDb]({links['tmdb']})")
            # if your service does not support markdown link format, uncomment the next line
            #links_section.append(f"• TMDb: {links['tmdb']}")

        trailers = message.get("trailer") or []
        if len(trailers) == 1:
            links_section.append(f"[Trailer]({trailers[0]})")
        elif len(trailers) >= 2:
            links_section.append(f"[Trailer FR]({trailers[0]})")
            links_section.append(f"[Trailer EN]({trailers[1]})")
            # if your service does not support markdown link format, uncomment the next lines
            #links_section.append(f"• Trailer FR: {trailers[0]}")
            #links_section.append(f"• Trailer EN: {trailers[1]}")

        if links_section:
            message_parts.append("\n" + "\n".join(links_section))

        return "\n".join(message_parts)

    except Exception as e:
        logging.error(f"Error formatting message for Matrix: {e}", exc_info=True)
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
        if not message:
            return ""

        trailers = message.get("trailer") or []
        if len(trailers) == 1:
            trailer_text = f'<br><a href="{trailers[0]}">Trailer</a>'
        elif len(trailers) >= 2:
            trailer_text = f'<br><a href="{trailers[0]}">Trailer FR</a><br><a href="{trailers[1]}">Trailer EN</a>'
        else:
            trailer_text = ""

        links = message.get("media_link", {}) or {}
        link_text = ""
        if "imdb" in links and links["imdb"]:
            link_text += f'<br><br><a href="{links["imdb"]}">IMDb</a>'
        if "tmdb" in links and links["tmdb"]:
            link_text += f'<br><a href="{links["tmdb"]}">TMDb</a>'

        formatted_message = ""
        if message.get("title"):
             formatted_message += f'<h1>{message.get("title")}</h1><br/>'

        if message.get('description'):
            formatted_message += f'<pre>{message.get("description")}</pre>'

        formatted_message += link_text
        formatted_message += trailer_text
        return formatted_message

    except Exception as e:
        logging.error(f"Error formatting message: {e}", exc_info=True)
        return ""

def upload_image(image_path: str) -> str:
    """
    Upload image to the Matrix server.

    Args:
        image_path (str): The local path to the image.

    Returns:
        str: The content URI of the uploaded image.
    """
    if not os.path.exists(image_path):
        logging.error(f"Image path does not exist: {image_path}")
        return ""

    try:
        url = f"{MATRIX_URL}/_matrix/media/r0/upload?filename={os.path.basename(image_path)}"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "image/jpeg"
        }
        with open(image_path, 'rb') as image_file:
            response = requests.post(url, headers=headers, data=image_file)

        response.raise_for_status()
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
    if options is None:
        options = {}

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        # Check if we need to send the image
        send_image = options.get('send_image')
        image_path = options.get('picture_path')
        if send_image:
            if not image_path:
                logging.error("send_image is True but picture_path is missing.")
            else:
                # Upload the image and get the content URI
                image_uri = upload_image(image_path)
                if image_uri:
                    # Send the image message
                    send_image_url = f"{MATRIX_URL}/_matrix/client/r0/rooms/{ROOM_ID}/send/m.room.message"
                    image_info = {
                        "msgtype": "m.image",
                        "body": os.path.basename(image_path),
                        "url": image_uri,
                        "info": {
                            "mimetype": "image/jpeg"
                        }
                    }
                    # resolution not hardcoded, let matrix handle this
                    # "info": {"size": os.path.getsize(image_path), "w": 342, "h": 513}

                    response = requests.post(send_image_url, headers=headers, json=image_info)
                    response.raise_for_status()
                    logging.info("Image sent successfully to Matrix.")
                else:
                    logging.error("Failed to upload image, skipping image sending.")

        # Send the formatted text message
        formatted_message = format_message(message)
        #html_formatted_message = html_format_message(message) # Optionnel, car vous ne l'utilisez pas

        if not formatted_message:
            logging.warning("Formatted message is empty, not sending text message.")
            return None # Ne rien envoyer si le message est vide

        # Send the formatted message
        send_text_url = f"{MATRIX_URL}/_matrix/client/r0/rooms/{ROOM_ID}/send/m.room.message"
        # associated documentation: https://spec.matrix.org/latest/client-server-api/#send-m-room-message
        # changed from m.notice to m.text and comment format and formatted_body as I encounter issue sending message.
        text_info = {
            "msgtype": "m.text", # m.notice: for automated client, no answer expected
            "body": formatted_message, # notice text to send. Plain text, if html client formatting is not supported
            #"format": "org.matrix.custom.html", # format used in formatted_body
            #"formatted_body": html_formatted_message # formatted version of body. Required if format is specified
        }
        response = requests.post(send_text_url, headers=headers, json=text_info)
        response.raise_for_status()
        logging.info("Text message sent successfully to Matrix.")

        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to Matrix: {e}")
        if e.response:
            logging.error(f"Response body: {e.response.text}")
        return None

if __name__ == "__main__":
    message = {
        "title": "Example Title",
        "description": "Example Description",
        "trailer": ["http://example.com/trailer1", "http://example.com/trailer2"],
        "media_link": {
            "imdb": "http://example.com/imdb",
            "tmdb": "http://example.com/tmdb"
        },
        "technical_details": {
            "video": {"resolution": "1080p", "codec": "H.265", "hdr": "HDR10"},
            "audio": ["DTS-HD MA 5.1", "AC3 5.1"],
            "subtitles": ["Français", "English"]
        }
    }

    image_url = "https://image.tmdb.org/t/p/w342/t1i10ptOivG4hV7erkX3tmKpiqm.jpg"
    local_image_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            local_image_path = tmp_file.name

        logging.info(f"Image downloaded to temporary path: {local_image_path}")

        options = {
            "send_image": True,
            "picture_path": local_image_path
        }
        response = send_message(message, options)
        if response:
            logging.info(f"Response Status Code: {response.status_code}")
        else:
            logging.error("Failed to send message")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download image from URL {image_url}: {e}")
    finally:
        if local_image_path and os.path.exists(local_image_path):
            os.remove(local_image_path)
            logging.info(f"Removed temporary image file: {local_image_path}")

