#!/usr/bin/env python3

import re
import os
import logging
from config.settings import TMDB_API_KEY, LANGUAGE, LANGUAGE2, BASE_URL
from utils.media_details import get_tmdb_details, imdb_to_tmdb, get_trailer_link
from utils.download import download_and_get_poster_by_id

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')

def handle_media(data: dict) -> dict:
    """
    Manage media data and format the message.

    Args:
        data (dict): The media data.

    Returns:
        dict: The formatted message and options.

    """
    media_type = data.get('media_type', '')
    title = data.get('title', '')
    imdb = data.get('imdb', '')
    tmdb = data.get('tmdb', '')

    message = {}
    send_image = False
    picture_path = None

    if is_season_ep_or_movie(media_type, title) == "movie":
        # It's a movie
        if imdb:
            tmdb = imdb_to_tmdb(imdb)
        tmdb_details = get_tmdb_details(media_type, tmdb, language=LANGUAGE)
        title = tmdb_details.get('title', '')
        release_date = tmdb_details.get('release_date', '')
        formatted_title = f"{title} ({release_date.split('-')[0]})" if release_date else title
        overview = tmdb_details.get('overview', '')
        poster_id = tmdb_details.get('poster_path', '')
        picture_path = download_and_get_poster_by_id(poster_id)
        trailer = get_trailer_link(media_type, tmdb)
        #mdb_links = {
        media_link = {
            "imdb": f"https://imdb.com/title/{imdb}",
            "tmdb": f"https://tmdb.org/{media_type}/{tmdb}"
        }
        #imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
        #tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}"
        #media_link = imdb_link + "\n" + tmdb_link
        message = format_message(formatted_title, overview, media_link, trailer)
        send_image = True
    elif is_season_ep_or_movie(media_type, title) == "season":
        # It's a season
        season_name = re.search(r"Season-added:\s*([^,]+)", title, flags=re.IGNORECASE).group(1)
        season_number = re.search(r", Saison\s*([0-9]+)", title, flags=re.IGNORECASE).group(1)
        formatted_title = season_name + ", Saison " + season_number
        message = format_message(formatted_title, "", None, None)
    elif is_season_ep_or_movie(media_type, title) == "episode":
        # It's an episode
        formatted_title = re.search(r"Episode-added:\s*(.*)", title, flags=re.IGNORECASE).group(1)
        if imdb:
            media_link = {
                "imdb": f"https://imdb.com/title/{imdb}",
                "tmdb": f"{imdb_to_tmdb(imdb)}"
            }
            #imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
            #tmdb_link = f"• TMDb: {imdb_to_tmdb(imdb)}"
            #media_link = imdb_link + "\n" + tmdb_link
        else:
            media_link = None
        message = format_message(formatted_title, "", media_link, None)
    elif is_season_ep_or_movie(media_type, title) == "serie":
        # It's a series or other (documentary for example)
        if not tmdb and not imdb:
            message = format_message(title, "", None, None)
        else:
            tmdb_details = get_tmdb_details(media_type, tmdb, language=LANGUAGE)
            title = tmdb_details.get('name', '')
            release_date = tmdb_details.get('first_air_date', '')
            formatted_title = f"{title} ({release_date.split('-')[0]})" if release_date else title
            overview = tmdb_details.get('overview', '')
            poster_id = tmdb_details.get('poster_path', '')
            picture_path = download_and_get_poster_by_id(poster_id)
            trailer = get_trailer_link(media_type, tmdb)
            media_link = {
                "imdb": f"https://imdb.com/title/{imdb}",
                "tmdb": f"https://tmdb.org/{media_type}/{tmdb}" if tmdb else f"{imdb_to_tmdb(imdb)}"
            }
            #imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
            #tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}" if tmdb else f"• TMDb: {imdb_to_tmdb(imdb)}"
            #media_link = imdb_link + "\n" + tmdb_link
            message = format_message(formatted_title, overview, media_link, trailer)
            send_image = True

    return {"message": message, "send_image": send_image, "picture_path": picture_path}

def format_title(title: str, release_date: str) -> str:
    """
    Format title with release year if available.

    Args:
        title (str): Title of the media.
        release_date (str): Release date of the media.

    Returns:
        str: Formatted title.
    """
    return f"{title} ({release_date.split('-')[0]})" if release_date else title

def extract_season_info(title: str) -> (str, str):
    """
    Extract season name and number from title.

    Args:
        title (str): Title containing season information.

    Returns:
        tuple: Season name (str), season number (str).
    """
    season_name = re.search(r"Season-added:\s*([^,]+)", title, flags=re.IGNORECASE).group(1)
    season_number = re.search(r", Saison\s*([0-9]+)", title, flags=re.IGNORECASE).group(1)
    return season_name, season_number

def format_media_links(imdb: str, media_type: str, tmdb: str) -> str:
    """
    Format media links for IMDb and TMDB.

    Args:
        imdb (str): IMDb ID of the media.
        media_type (str): Type of media (movie, tv).
        tmdb (str): TMDB ID of the media.

    Returns:
        str: Formatted media links.
    """
    imdb_link = f"• IMDb: https://imdb.com/title/{imdb}" if imdb else ""
    tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}" if tmdb else f"• TMDb: {imdb_to_tmdb(imdb)}"
    return imdb_link + "\n" + tmdb_link

def handle_serie(imdb: str, tmdb: str, media_type: str):
    """
    Handle processing for series.

    Args:
        imdb (str): IMDb ID of the series.
        tmdb (str): TMDB ID of the series.
        media_type (str): Type of media (tv).

    Returns:
        tuple: Formatted title (str), overview (str), path to poster (str), trailer link (str), media links (str).
    """
    tmdb_details = get_tmdb_details(media_type, tmdb)
    title = tmdb_details.get('name', '')
    release_date = tmdb_details.get('first_air_date', '')
    formatted_title = format_title(title, release_date)
    overview = tmdb_details.get('overview', '')
    poster_id = tmdb_details.get('poster_path', '')
    poster_path = download_and_get_poster_by_id(poster_id)
    trailer = get_trailer_link(media_type, tmdb)
    media_link = format_media_links(imdb, media_type, tmdb)
    return formatted_title, overview, poster_path, trailer, media_link

def is_season_ep_or_movie(media_type: str, title: str) -> str:
    """
    Check if the media is a season, episode, or movie.

    Args:
        media_type (str): Type of media (movie, tv).
        title (str): Title of the media.

    Returns:
        str: Type of media (season, episode, movie, or serie).
    """
    if media_type == "movie":
        return "movie"
    elif media_type == "tv":
        if re.search(r"Season-added\s*", title, flags=re.IGNORECASE):
            return "season"
        elif re.search(r"Episode-added\s*", title, flags=re.IGNORECASE):
            return "episode"
        else:
            return "serie"
    return None

def format_message(title: str, overview: str, media_link: dict = None, trailer: list = None) -> dict:
    """
    Format the message to be sent.

    Args:
        title (str): The title of the media.
        overview (str): The synopsis of the media.
        media_link (dict): The links to the media (IMDb, TMDb).
        trailer (list, optional): The link(s) to the trailer.

    Returns:
        dict: The formatted message.
    """
    message = {
        "title": title,
        "description": overview,
        "media_link": media_link,
        "trailer": trailer
    }
    return message

def send_to_all_connectors(connectors:dict, message: dict, options: dict):
    """
    Send the formatted message to all connectors.

    Args:
        connectors (dict): The loaded connectors
        message (dict): Message to be sent.
        options (dict): Additional options for the message
    """
    for connector_name, connector_module in connectors.items():
        try:
            response = connector_module.send_message(message, options)
            if response:
                logging.info(f"Message sent to {connector_name} successfully.")
        except Exception as e:
            logging.error(f"Failed to send message to {connector_name}: {e}")

if __name__ == "__main__":
    # Example usage of handle_media function
    data = {
        "media_type": "movie",
        "title": "Example Movie",
        "imdb": "tt1234567",
        "tmdb": "550"
    }
    result = handle_media(data)
    print(result)

    # Example usage of send_to_all_connectors function
    connectors = {
        'whatsapp': {
            'send_message': lambda message, options: print(f"Sending via WhatsApp: {message}, options: {options}")
        },
        'slack': {
            'send_message': lambda message, options: print(f"Sending via Slack: {message}, options: {options}")
        }
    }
    send_to_all_connectors(connectors, message, options)


