#!/usr/bin/env python3

import requests
import tempfile
import logging

def download_and_get_poster_by_id(poster_id: str) -> str:
    """
    Download the poster by ID and return the file path.

    Args:
        poster_id (str): ID of the poster.

    Returns:
        str: Path to the downloaded poster.
    """
    # all availables size: https://api.themoviedb.org/3/configuration
    poster_url = f"https://image.tmdb.org/t/p/w342/{poster_id}"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
            response = requests.get(poster_url)
            response.raise_for_status()
            temp.write(response.content)
            temp_path = temp.name
        return temp_path
    except requests.RequestException as e:
        logging.error(f"Error downloading poster: {e}")
        return ""

if __name__ == "__main__":
    poster_id = "t1i10ptOivG4hV7erkX3tmKpiqm.jpg"
    print("open",download_and_get_poster_by_id(poster_id))

