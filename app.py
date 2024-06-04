#!/usr/bin/env python3

from flask import Flask, request, jsonify
from utils.media_details import get_tmdb_details, imdb_to_tmdb, get_trailer_link, is_season_ep_or_movie
from utils.download import download_and_get_poster_by_id
from integrations.whatsapp.whatsapp import send_whatsapp_message
import os
import re

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def receive_data():
    if not request.is_json:
        return jsonify({'message': 'Data is not json!'}), 400

    data = request.json
    media_type = data.get('media_type', '')
    title = data.get('title', '')
    imdb = data.get('imdb', '')
    tmdb = int(data.get('tmdb', ''))

    poster_path = None

    if is_season_ep_or_movie(media_type, title) == "movie":
        tmdb_details = get_tmdb_details(media_type, tmdb)
        title = tmdb_details.get('title', '')
        release_date = tmdb_details.get('release_date', '')
        formatted_title = f"{title} ({release_date.split('-')[0]})" if release_date else title
        overview = tmdb_details.get('overview', '')
        poster_id = tmdb_details.get('poster_path', '')
        poster_path = download_and_get_poster_by_id(poster_id)
        trailer = get_trailer_link(media_type, tmdb)
        imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
        tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}"
        media_link = imdb_link + "\n" + tmdb_link
        fmessage = format_message(formatted_title, overview, media_link, trailer)
        send_whatsapp_message(fmessage, True, poster_path)
    elif is_season_ep_or_movie(media_type, title) == "season":
        season_name = re.search(r"Season-added:\s*([^,]+)", title, flags=re.IGNORECASE).group(1)
        season_number = re.search(r", Saison\s*([0-9]+)", title, flags=re.IGNORECASE).group(1)
        title = season_name + ", Saison " + season_number
        fmessage = format_message(title, "", "", "")
        send_whatsapp_message(fmessage, False, None)
    elif is_season_ep_or_movie(media_type, title) == "episode":
        title = re.search(r"Episode-added:\s*(.*)", title, flags=re.IGNORECASE).group(1)
        if imdb != '':
            imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
            tmdb_link = f"• TMDb: {imdb_to_tmdb(imdb)}"
            media_link = imdb_link + "\n" + tmdb_link
        else:
            media_link = ""
        fmessage = format_message(title, "", media_link, "")
        send_whatsapp_message(fmessage, False, None)
    elif is_season_ep_or_movie(media_type, title) == "serie":
        if tmdb == "" and imdb == "":
            fmessage = format_message(title, "", "", "")
            send_whatsapp_message(fmessage, False, None)
        else:
            tmdb_details = get_tmdb_details(media_type, tmdb)
            title = tmdb_details.get('name', '')
            release_date = tmdb_details.get('first_air_date', '')
            formatted_title = f"{title} ({release_date.split('-')[0]})" if release_date else title
            overview = tmdb_details.get('overview', '')
            poster_id = tmdb_details.get('poster_path', '')
            poster_path = download_and_get_poster_by_id(poster_id)
            trailer = get_trailer_link(media_type, tmdb)
            imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
            tmdb_link = f"• TMDb: {imdb_to_tmdb(imdb)}" if tmdb == "" else f"• TMDb: https://tmdb.org/{media_type}/{tmdb}"
            media_link = imdb_link + "\n" + tmdb_link
            fmessage = format_message(formatted_title, overview, media_link, trailer)
            send_whatsapp_message(fmessage, True, poster_path)

    if poster_path:
        os.remove(poster_path)

    return jsonify({'message': 'Data received successfully!'})

def format_message(title: str, overview: str, media_link: str, trailer: bool = False) -> str:
    """
    Format the message to be sent.

    Args:
        title (str): Title of the media.
        overview (str): Overview of the media.
        media_link (str): imdb/tmdb links to the media.
        trailer (bool, optional): Whether to include the trailer link(s). Defaults to False.

    Returns:
        str: Formatted message.
    """
    message = f"*{title}*\n"
    if overview:
        message += f"```{overview}```\n"
    if media_link:
        message += f"{media_link}\n"
    if trailer:
        message += trailer
    return message

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7778)

