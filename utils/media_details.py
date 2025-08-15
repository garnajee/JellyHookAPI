#!/usr/bin/env python3
import requests
import re
import logging
from config.settings import TMDB_API_KEY, LANGUAGE, LANGUAGE2, BASE_URL, JELLYFIN_API_URL, JELLYFIN_API_KEY, JELLYFIN_USER_ID

def get_tmdb_details(media_type: str, tmdbid: str, language: str = LANGUAGE) -> dict:
    """
    Get details from TMDB API.

    Args:
        media_type (str): Type of media (movie, tv).
        tmdbid (str): TMDB ID of the media.
        language (str, optional): Language for the details. Defaults to LANGUAGE.

    Returns:
        dict: Details of the media.
    """
    url = f"{BASE_URL}/{media_type}/{tmdbid}"
    
    params_primary = {
        'api_key': TMDB_API_KEY,
        'language': language,
    }
    
    params_secondary = {
        'api_key': TMDB_API_KEY,
        'language': LANGUAGE2,
    }
    
    try:
        response_primary = requests.get(url, params=params_primary, timeout=10)
        response_primary.raise_for_status()
        details = response_primary.json()

        # If details are incomplete, fetch with the secondary language
        if any(not details.get(key) for key in details):
            response_secondary = requests.get(url, params=params_secondary, timeout=10)
            response_secondary.raise_for_status()
            details_secondary = response_secondary.json()

            # Fill in any empty fields from the secondary language
            for key, value in details_secondary.items():
                if not details.get(key):
                    details[key] = value

    except requests.RequestException as e:
        logging.error(f"Error fetching TMDB details: {e}")
        return {}

    return details

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

def get_trailer_link(media_type: str, tmdbid: str) -> list:
    """
    Get the Youtube trailer link.

    Args:
        media_type (str): Type of media (movie, tv).
        tmdbid (str): TMDB ID of the media.

    Returns:
        list: Trailer link(s).
    """
    languages = [(LANGUAGE, r"bande[-\s]?annonce"), (LANGUAGE2, r"trailer")]
    trailer_links = []
    vidt = f"{media_type}/{tmdbid}"
    for language, pattern in languages:
        youtube_key = search_trailer_key(vidt, language, pattern)
        if youtube_key:
            trailer_links.append(f"https://youtu.be/{youtube_key}")
    return trailer_links

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

def analyze_french_version(display_title: str, language_code: str) -> str:
    """
    Analyzes the display title and language code to determine if it's VFF or VFQ.

    Args:
        display_title (str): The display title of the stream (e.g., "Français (TrueFrench) DTS-HD MA 5.1").
        language_code (str): The 3-letter language code (e.g., "fre").

    Returns:
        str: A formatted language label (e.g., "FR (VFF)", "FR (VFQ)", or the original code).
    """
    lang_code_upper = (language_code or "").upper()
    if lang_code_upper not in ['FRE', 'FRA']:
        return lang_code_upper

    title_lower = (display_title or "").lower()

    keywords_vfq = ['vfq', 'fr-ca', 'ca', 'canadian', 'canadien']
    keywords_vff = ['vff', 'truefrench', 'fr-fr', 'european', "vfi", "france"]

    if any(keyword in title_lower for keyword in keywords_vfq):
        return "🇨🇦 VFQ"
    
    if any(keyword in title_lower for keyword in keywords_vff):
        return "🇫🇷 VFF"
    return "FR"

def get_jellyfin_media_details(item_id: str) -> dict:
    """
    Get media details from Jellyfin API, with enhanced French version detection.

    Args:
        item_id (str): The ID of the media item in Jellyfin.

    Returns:
        dict: A dictionary containing formatted technical details of the media.
    """
    if not all([JELLYFIN_API_URL, JELLYFIN_API_KEY, JELLYFIN_USER_ID]):
        logging.warning("Jellyfin API URL, Key, or User ID is not set. Skipping Jellyfin details.")
        return {}

    headers = {
        'X-Emby-Token': JELLYFIN_API_KEY
    }
    url = f"{JELLYFIN_API_URL}/Users/{JELLYFIN_USER_ID}/Items/{item_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        media_streams = data.get('MediaStreams', [])
        if not media_streams:
            return {}

        details = {
            'video': {},
            'audio': [],
            'subtitles': []
        }

        # Video details
        video_stream = next((s for s in media_streams if s.get('Type') == 'Video'), None)
        if video_stream:
            width = video_stream.get('Width')
            height = video_stream.get('Height')

            resolution_label = ""
            if width == 3840:
                resolution_label = "2160p"
            elif width == 1920:
                resolution_label = "1080p"
            elif width == 1280:
                resolution_label = "720p"
            else:
                if height:
                    resolution_label = f"{height}p"
                else:
                    resolution_label = "N/A"

            details['video']['resolution'] = resolution_label
            details['video']['codec'] = video_stream.get('Codec', 'N/A').upper()
            if video_stream.get('VideoRange') == 'HDR':
                details['video']['hdr'] = "HDR"

        # Audio details
        for stream in media_streams:
            if stream.get('Type') == 'Audio':
                language_label = analyze_french_version(
                    stream.get('DisplayTitle'), 
                    stream.get('Language')
                )
                details['audio'].append(language_label)
                
        # Subtitle details
        for stream in media_streams:
            if stream.get('Type') == 'Subtitle':
                language_label = analyze_french_version(
                    stream.get('DisplayTitle'), 
                    stream.get('Language')
                )
                details['subtitles'].append(language_label)
                
        # Handle duplicates
        if details['audio']:
            details['audio'] = list(dict.fromkeys(details['audio']))
        if details['subtitles']:
            details['subtitles'] = list(dict.fromkeys(details['subtitles']))

        # Handle empty lists
        if not details['audio']:
            details.pop('audio')
        if not details['subtitles']:
            details.pop('subtitles')

        return details

    except requests.RequestException as e:
        logging.error(f"Error fetching Jellyfin media details for item {item_id}: {e}")
        return {}

if __name__ == "__main__":
    media_type = "movie"
    tmdbid = "550"
    print(get_tmdb_details(media_type, tmdbid))
    imdb_id = "tt0137523"
    print(imdb_to_tmdb(imdb_id))
    print(get_trailer_link(media_type, tmdbid))
    title = "Season-added: The Mandalorian, Saison 2"
    print(is_season_ep_or_movie("tv", title))

