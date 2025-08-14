import requests
import json
import logging
from utils.media_details import get_jellyfin_media_details

# --- PLEASE FILL IN YOUR DETAILS HERE ---
# Find your UserId by going to your Jellyfin Dashboard > Users, clicking on your profile,
# and copying the ID from the URL (e.g., .../user?userId=xxxxxxxx).
# Find an ItemId by navigating to any movie or episode, clicking the three-dot menu,
# selecting "Info", and copying the ID from there.
JELLYFIN_API_URL = "http://your_jellyfin_url:8096"  # e.g., "http://192.168.1.10:8096"
JELLYFIN_API_KEY = "your_jellyfin_api_key"
TEST_ITEM_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
TEST_USER_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
# -----------------------------------------

# --- DO NOT EDIT BELOW THIS LINE ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def direct_api_call(url, headers):
    """Makes a direct API call and returns the raw JSON."""
    logging.info(f"Making direct API call to: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info("Direct API call successful.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Direct API call failed: {e}")
        if 'response' in locals() and response.content:
            logging.error(f"Response content: {response.content.decode('utf-8')}")
        return None

def run_debug():
    """Runs the debugging script."""
    if JELLYFIN_API_URL == "http://your_jellyfin_url:8096" or JELLYFIN_API_KEY == "your_jellyfin_api_key":
        logging.error("Please fill in your Jellyfin URL and API Key in the script.")
        return

    # --- Part 1: Direct API Call to get raw data ---
    logging.info("--- PART 1: DIRECT API CALL ---")
    direct_url = f"{JELLYFIN_API_URL}/Users/{TEST_USER_ID}/Items/{TEST_ITEM_ID}"
    headers = {'X-Emby-Token': JELLYFIN_API_KEY}

    raw_data = direct_api_call(direct_url, headers)

    if raw_data:
        print("\n--- RAW JSON RESPONSE (from direct call) ---")
        print(json.dumps(raw_data, indent=2))
        print("------------------------------------------\n")
    else:
        logging.error("Could not retrieve raw data. Aborting further tests.")
        return

    # --- Part 2: Testing the get_jellyfin_media_details function ---
    # We need to temporarily set the environment variables for the function to use them
    from config import settings
    settings.JELLYFIN_API_URL = JELLYFIN_API_URL
    settings.JELLYFIN_API_KEY = JELLYFIN_API_KEY

    logging.info("--- PART 2: TESTING get_jellyfin_media_details FUNCTION ---")
    formatted_details = get_jellyfin_media_details(TEST_ITEM_ID, TEST_USER_ID)

    if formatted_details:
        print("\n--- FORMATTED DETAILS (from function) ---")
        print(json.dumps(formatted_details, indent=2))
        print("---------------------------------------\n")
    else:
        logging.error("The get_jellyfin_media_details function returned an empty dictionary.")

if __name__ == "__main__":
    run_debug()
