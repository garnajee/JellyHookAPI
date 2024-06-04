#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Default languages
LANGUAGE = os.getenv("LANGUAGE", "fr-FR")
LANGUAGE2 = os.getenv("LANGUAGE2", "en-US")

# Base URL for TMDB API
BASE_URL = "https://api.themoviedb.org/3"

