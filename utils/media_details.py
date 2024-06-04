#!/usr/bin/env python3
import requests
import re
import logging
from config.settings import TMDB_API_KEY, LANGUAGE, LANGUAGE2, BASE_URL

def get_tmdb_details(media_type: str, tmdbid: int, language: str = LANGUAGE) -> dict:
    """
    Get details from TMDB API.

    Args:
        media_type (str): Type of media (movie, tv).
        tmdbid (int): TMDB ID of the media.
        language (str, optional): Language for the details. Defaults to LANGUAGE.

    Returns:
        dict: Details of the media.
    """
    url = f"{BASE_URL}/{media_type}/{tmdbid}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching TMDB details: {e}")
        return {}

def imdb_to_tmdb(imdb_id: str) -> str:
    """
    Get TMDB ID from IMDb ID.

    Args:
        imdb_id (str): IMDb ID of the media.

    Returns:
        str: TMDB link.
    """
    url = f"{BASE_URL}/find/{imdb_id}?external_source=imdb_id&language={LANGUAGE}&api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()
        if "movie_results" in results and results["movie_results"]:
            return f"https://tmdb.org/movie/{results['movie_results'][0]['id']}"
        elif "tv_results" in results and results["tv_results"]:
            return f"https://tmdb.org/tv/{results['tv_results'][0]['id']}"
        elif "tv_episode_results" in results and results["tv_episode_results"]:
            return f"https://tmdb.org/tv/episode/{results['tv_episode_results'][0]['id']}"
    except requests.RequestException as e:
        logging.error(f"Error fetching TMDB link from IMDb ID: {e}")
    return None

def get_trailer_link(media_type: str, tmdbid: int) -> str:
    """
    Get the Youtube trailer link.

    Args:
        media_type (str): Type of media (movie, tv).
        tmdbid (int): TMDB ID of the media.

    Returns:
        str: Trailer link.
    """
    languages = [(LANGUAGE, r"bande[-\s]?annonce"), (LANGUAGE2, r"trailer")]
    trailer_links = []
    vidt = f"{media_type}/{tmdbid}"
    for language, pattern in languages:
        youtube_key = search_trailer_key(vidt, language, pattern)
        if youtube_key:
            trailer_links.append(f"https://youtu.be/{youtube_key}")
    if trailer_links:
        if len(trailer_links) == 2:
            return f"• Trailer FR: {trailer_links[0]}\n • Trailer EN: {trailer_links[1]}"
        elif len(trailer_links) == 1:
            return f"• Trailer: {trailer_links[0]}\n"
    return ""

def search_trailer_key(vidt: str, language: str, pattern: str) -> str:
    """
    Search for the trailer key in the TMDB API.

    Args:
        vidt (str): Video type and ID.
        language (str): Language for the search.
        pattern (str): Regex pattern to search for.

    Returns:
        str: Trailer key if found, None otherwise.
    """
    regex = re.compile(r"^[a-z]+/[0-9]+")
    if "season" in vidt:
        vidt = regex.findall(vidt)[0]
    url = f"{BASE_URL}/{vidt}/videos"
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            for video in results:
                if re.search(pattern, video.get("name", ""), flags=re.IGNORECASE):
                    return video.get("key")
    except requests.RequestException as e:
        logging.error(f"Error fetching trailer key: {e}")
    return None

def is_season_ep_or_movie(media_type: str, title: str) -> str:
    """
    Check if it's a season, episode or a movie.

    Args:
        media_type (str): Type of media (movie, tv).
        title (str): Title of the media.

    Returns:
        str: "season", "episode" or "movie".
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

if __name__ == "__main__":
    media_type = "movie"
    tmdbid = "550"
    print(get_tmdb_details(media_type, tmdbid))
    imdb_id = "tt0137523"
    print(imdb_to_tmdb(imdb_id))
    print(get_trailer_link(media_type, tmdbid))
    title = "Season-added: The Mandalorian, Saison 2"
    print(is_season_ep_or_movie("tv", title))

