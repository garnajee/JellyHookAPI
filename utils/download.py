#!/usr/bin/env python3

import requests
import tempfile

def download_and_get_poster_by_id(poster_id: str) -> str:
    """
    Download the poster by ID and return the file path.

    Args:
        poster_id (str): ID of the poster.

    Returns:
        str: Path to the downloaded poster.
    """
    poster_url = f"https://image.tmdb.org/t/p/w342/{poster_id}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        response = requests.get(poster_url)
        temp.write(response.content)
        temp_path = temp.name
    return temp_path

if __name__ == "__main__":
    poster_id = "t1i10ptOivG4hV7erkX3tmKpiqm.jpg"
    print("open",download_and_get_poster_by_id(poster_id))

