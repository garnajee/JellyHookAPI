#!/usr/bin/env python3

import re
import os
from utils.media_details import get_tmdb_details, imdb_to_tmdb, get_trailer_link
from utils.download import download_and_get_poster_by_id

def handle_media(media_type: str, title: str, imdb: str, tmdb: int):
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
    return f"{title} ({release_date.split('-')[0]})" if release_date else title

def extract_season_info(title: str) -> (str, str):
    season_name = re.search(r"Season-added:\s*([^,]+)", title, flags=re.IGNORECASE).group(1)
    season_number = re.search(r", Saison\s*([0-9]+)", title, flags=re.IGNORECASE).group(1)
    return season_name, season_number

def format_media_links(imdb: str, media_type: str, tmdb: int) -> str:
    imdb_link = f"• IMDb: https://imdb.com/title/{imdb}" if imdb else ""
    tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}" if tmdb else f"• TMDb: {imdb_to_tmdb(imdb)}"
    return imdb_link + "\n" + tmdb_link

def handle_serie(imdb: str, tmdb: int, media_type: str):
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
    message = f"*{title}*\n"
    if overview:
        message += f"```{overview}```\n"
    if media_link:
        message += f"{media_link}\n"
    if trailer:
        message += trailer
    return message

def send_to_all_connectors(connectors: dict, message: str, send_image: bool = False, picture_path: str = None):
    for name, connector in connectors.items():
        if hasattr(connector, 'send_message'):
            if name == 'whatsapp':
                phone = "PHONE_NUMBER"  # Replace with actual phone number or pass it appropriately
                connector.send_message(phone, message, send_image, picture_path)
            elif name == 'slack':
                channel = "CHANNEL_NAME"  # Replace with actual channel name or pass it appropriately
                connector.send_message(channel, message)
            # Add more conditions for other connectors if needed


