#!/usr/bin/env python3

import re
import os
from utils.media_details import get_tmdb_details, imdb_to_tmdb, get_trailer_link
from utils.download import download_and_get_poster_by_id

def handle_media(media_type: str, title: str, imdb: str, tmdb: int):
    """
    Handle media processing based on type and title.

    Args:
        media_type (str): Type of media (movie, tv).
        title (str): Title of the media.
        imdb (str): IMDb ID of the media.
        tmdb (int): TMDB ID of the media.

    Returns:
        tuple: Formatted message (str), send_image flag (bool), path to poster (str).
    """
    poster_path = None

    if is_season_ep_or_movie(media_type, title) == "movie":
        tmdb_details = get_tmdb_details(media_type, tmdb)
        formatted_title = format_title(tmdb_details.get('title', ''), tmdb_details.get('release_date', ''))
        overview = tmdb_details.get('overview', '')
        poster_id = tmdb_details.get('poster_path', '')
        poster_path = download_and_get_poster_by_id(poster_id)
        trailer = get_trailer_link(media_type, tmdb)
        media_link = format_media_links(imdb, media_type, tmdb)
        fmessage = format_message(formatted_title, overview, media_link, trailer)
        return fmessage, True, poster_path
    elif is_season_ep_or_movie(media_type, title) == "season":
        season_name, season_number = extract_season_info(title)
        formatted_title = f"{season_name}, Saison {season_number}"
        fmessage = format_message(formatted_title, "", "", "")
        return fmessage, False, None
    elif is_season_ep_or_movie(media_type, title) == "episode":
        episode_title = re.search(r"Episode-added:\s*(.*)", title, flags=re.IGNORECASE).group(1)
        media_link = format_media_links(imdb, media_type, tmdb)
        fmessage = format_message(episode_title, "", media_link, "")
        return fmessage, False, None
    elif is_season_ep_or_movie(media_type, title) == "serie":
        formatted_title, overview, poster_path, trailer, media_link = handle_serie(imdb, tmdb, media_type)
        fmessage = format_message(formatted_title, overview, media_link, trailer)
        return fmessage, True, poster_path
    return None, False, None

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

def format_media_links(imdb: str, media_type: str, tmdb: int) -> str:
    """
    Format media links for IMDb and TMDB.

    Args:
        imdb (str): IMDb ID of the media.
        media_type (str): Type of media (movie, tv).
        tmdb (int): TMDB ID of the media.

    Returns:
        str: Formatted media links.
    """
    imdb_link = f"• IMDb: https://imdb.com/title/{imdb}" if imdb else ""
    tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}" if tmdb else f"• TMDb: {imdb_to_tmdb(imdb)}"
    return imdb_link + "\n" + tmdb_link

def handle_serie(imdb: str, tmdb: int, media_type: str):
    """
    Handle processing for series.

    Args:
        imdb (str): IMDb ID of the series.
        tmdb (int): TMDB ID of the series.
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

def format_message(title: str, overview: str, media_link: str, trailer: bool = False) -> str:
    """
    Format the message to be sent.

    Args:
        title (str): Title of the media.
        overview (str): Overview of the media.
        media_link (str): Links to media details.
        trailer (bool, optional): Whether to include trailer links. Defaults to False.

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

def send_to_all_connectors(connectors: dict, message: str, send_image: bool = False, picture_path: str = None):
    """
    Send the formatted message to all connectors.

    Args:
        connectors (dict): Dictionary of connectors.
        message (str): Message to be sent.
        send_image (bool, optional): Whether to send an image. Defaults to False.
        picture_path (str, optional): Path to the image file. Defaults to None.
    """
    for name, connector in connectors.items():
        if hasattr(connector, 'send_message'):
            options = {'send_image': send_image, 'picture_path': picture_path}
            connector.send_message(message, options)

if __name__ == "__main__":
    # Example usage of handle_media function
    media_type = "movie"
    title = "Example Movie"
    imdb = "tt1234567"
    tmdb = 550
    message, send_image, poster_path = handle_media(media_type, title, imdb, tmdb)
    print(message)
    print("Send image:", send_image)
    print("Poster path:", poster_path)

    # Example usage of send_to_all_connectors function
    connectors = {
        'whatsapp': {
            'send_message': lambda message, options: print(f"Sending via WhatsApp: {message}, options: {options}")
        },
        'slack': {
            'send_message': lambda message, options: print(f"Sending via Slack: {message}, options: {options}")
        }
    }
    send_to_all_connectors(connectors, message, send_image, poster_path)

