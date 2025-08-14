#!/usr/bin/env python3

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Default languages
LANGUAGE = os.getenv("LANGUAGE", "fr-FR")
LANGUAGE2 = os.getenv("LANGUAGE2", "en-US")

# Base URL for TMDB API
BASE_URL = "https://api.themoviedb.org/3"

# Jellyfin API configuration
JELLYFIN_API_URL = os.getenv("JELLYFIN_API_URL")
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")
JELLYFIN_USER_ID = os.getenv("JELLYFIN_USER_ID")
