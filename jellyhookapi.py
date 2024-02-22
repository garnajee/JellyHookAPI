#!/usr/bin/env python3

from flask import Flask, request, jsonify
import requests
import tempfile
import os
import re
from dotenv import load_dotenv

# load variables from .env file
load_dotenv()

# global variables
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
LANGUAGE = os.getenv("LANGUAGE")
LANGUAGE2 = os.getenv("LANGUAGE2")
base_url = "https://api.themoviedb.org/3"
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
WHATSAPP_API_USERNAME = os.getenv("WHATSAPP_API_USERNAME")
WHATSAPP_API_PWD = os.getenv("WHATSAPP_API_PWD")

app = Flask(__name__)

# function to send to whatsapp API
def send_whatsapp(phone, message, send_image=False, picture_path=None):
    # WhatsApp API Parameters
    url = f"{WHATSAPP_API_URL}/send/image" if send_image else f"{WHATSAPP_API_URL}/send/message"
    auth = (WHATSAPP_API_USERNAME, WHATSAPP_API_PWD)

    # WhatsApp API Headers
    headers = {'accept': 'application/json'}

    # WhatsApp API Data
    data = {'phone': phone}

    if send_image:
        # Send Image
        data['caption'] = message
        data['compress'] = "True"
        files = {'image': ('image', open(picture_path, 'rb'), 'image/png')}
    else:
        # Send Message
        data['message'] = message

    # Send the message to WhatsApp API
    response = requests.post(url, headers=headers, data=data, auth=auth, files=files if send_image else None)
    return response

def format_message(title, overview, media_link, trailer=False):
  message = f"*{title}*\n"
  
  #message += f"  → ajouté par {requestedBy_username}\n"
  
  if overview:
    message += f"```{overview}```\n"
  
  if media_link:
    message += f"{media_link}\n"
  
  if trailer:
    message += trailer

  return message

def download_and_get_poster_by_id(poster_id):
    poster_url = f"https://image.tmdb.org/t/p/w342/{poster_id}"
    
    # Download and save poster to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        response = requests.get(poster_url)
        temp.write(response.content)
        temp_path = temp.name

    return temp_path

def get_tmdb_details(media_type, tmdbid, language=LANGUAGE):
    # get details from tmdb API
    url = f"{base_url}/{media_type}/{tmdbid}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()

def get_trailer_link(media_type, tmdbid):
    # parameters
    global TMDB_API_KEY
    global LANGUAGE
    global LANGUAGE2
    global base_url
    
    # regex to search trailer depending on the language
    languages = [(LANGUAGE,r"bande[-\s]?annonce"), (LANGUAGE2,r"trailer")]
    trailer_links = []
    vidt = f"{media_type}/{tmdbid}"
    # search for the corresponding trailer depending on the language
    for language, pattern in languages:
        if vidt:
            youtube_key = search_trailer_key(vidt, language, pattern)
            if youtube_key:
                trailer_links.append(f"https://youtu.be/{youtube_key}")

    if trailer_links:
        if len(trailer_links) == 2:
            return f"• Trailer FR: {trailer_links[0]}\n • Trailer EN: {trailer_links[1]}"
        elif len(trailer_links) == 1:
            return f"• Trailer: {trailer_links[0]}\n"

# function to search for the trailer key in the tmdb API
def search_trailer_key(vidt, language, pattern):
    # parameters
    global TMDB_API_KEY
    global base_url

    regex = re.compile(r"^[a-z]+/[0-9]+")
    if "season" in vidt:
        vidt = regex.findall(vidt)[0]

    # search for the corresponding trailer depending on the language
    url = f"{base_url}/{vidt}/videos"
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

    except requests.exceptions.RequestException as e:
        print(f"search_trailer_key request error: {e}")

    return None # trailer key not found


def is_season_ep_or_movie(media_type,title):
    """
    Check if it's a season, episode or a movie

    :param media_type: media type (movie or tv, tv can be anything (serie or documentary) except movie)
    :param title: title of the media (contains "Season-added*" or "Episode-added*" or "{{Name}}*")
    :return: "season" if it's a season, "episode" if it's an episode, "movie" if it's a movie
    """
    if media_type == "movie":
        return "movie"
    elif media_type == "tv":
       # it's either a serie's name or an episode
       if re.search(r"Season-added\s*", title, flags=re.IGNORECASE):
          return "season"
       elif re.search(r"Episode-added\s*", title, flags=re.IGNORECASE):
          return "episode"
       else:
          # can be a serie or a something else (e.g. documentary)
          return "serie"
    else:
        return None
    
def imdb_to_tmdb(imdb_id):
    # get tmdb id from imdb id
    global TMDB_API_KEY
    global LANGUAGE
    global base_url

    url = f"{base_url}/find/{imdb_id}?external_source=imdb_id&language={LANGUAGE}&api_key={TMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        results = response.json()

        if "movie_results" in results and results["movie_results"]:
            vidt = f"movie/{results['movie_results'][0]['id']}"
            tmdb_link = f"https://tmdb.org/{vidt}"
            #return vidt, tmdb_link
            return tmdb_link
        elif "tv_results" in results and results["tv_results"]:
            vidt = f"tv/{results['tv_results'][0]['id']}"
            tmdb_link = f"https://tmdb.org/{vidt}"
            #return vidt, tmdb_link
            return tmdb_link
        elif "tv_episode_results" in results and results["tv_episode_results"]:
                tmdb_link = f"https://tmdb.org/tv/episode/{results['tv_episode_results'][0]['id']}"
                show_id = results['tv_episode_results'][0]['show_id']
                season_nb = results['tv_episode_results'][0]['season_number']
                episode_nb = results['tv_episode_results'][0]['episode_number']
                vidt =  f"tv/{show_id}/season/{season_nb}/episode/{episode_nb}"
                #return vidt, tmdb_link
                return tmdb_link
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None, None

@app.route('/api', methods=['POST'])
def receive_data():
  if not request.is_json:
    return jsonify({'message': 'Data is not json!'}), 400

  data = request.json
  media_type = data.get('media_type', '')
  title = data.get('title', '')
  imdb = data.get('imdb', '')
  tmdb = data.get('tmdb', '')

  poster_path = None

  if is_season_ep_or_movie(media_type,title) == "movie":
    # It's a movie
    tmdb_details = get_tmdb_details(media_type, tmdb, language=LANGUAGE)
    title = tmdb_details.get('title', '')
    overview = tmdb_details.get('overview', '')
    poster_id = tmdb_details.get('poster_path', '')
    poster_path = download_and_get_poster_by_id(poster_id)
    trailer = get_trailer_link(media_type, tmdb)
    imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
    tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}"
    media_link = imdb_link + "\n" + tmdb_link
    fmessage = format_message(title, overview, media_link, trailer)
    send_whatsapp(WHATSAPP_NUMBER, fmessage, True, poster_path)
  elif is_season_ep_or_movie(media_type,title) == "season":
    # It's a season
    # no overview, no poster, no trailer, media_link only
    # season name
    # extract info until "," (ex: "Season-added: The Mandalorian, Saison 2" should return "The Mandalorian"
    season_name = re.search(r"Season-added:\s*([^,]+)", title, flags=re.IGNORECASE).group(1)
    # season number
    season_number = re.search(r", Saison\s*([0-9]+)", title, flags=re.IGNORECASE).group(1)
    # final title
    title = season_name + ", Saison " + season_number
    # send message
    fmessage = format_message(title, "", "", "")
    send_whatsapp(WHATSAPP_NUMBER, fmessage, False, None)
  elif is_season_ep_or_movie(media_type,title) == "episode":
    # It's an episode
    # no overview, no poster, no trailer, media_link only
    # serie_name
    # remove "Episode-added: "
    title = re.search(r"Episode-added:\s*(.*)", title, flags=re.IGNORECASE).group(1)
    if imdb != '':
        # get epidode links (imdb + tmdb)
        imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
        # imdb to tmdb
        tmdb_link = f"• TMDb: {imdb_to_tmdb(imdb)}"
        media_link = imdb_link + "\n" + tmdb_link
    else:
        media_link = ""
    # send message
    fmessage = format_message(title, "", media_link, "")
    send_whatsapp(WHATSAPP_NUMBER, fmessage, False, None)
  elif is_season_ep_or_movie(media_type,title) == "serie":
    # It's a serie or something else (e.g. documentary)
    if tmdb == "" and imdb == "":
      # it's a documentary
      # no overview, no trailer, no media_link, no poster
      fmessage = format_message(title, "", "", "")
      send_whatsapp(WHATSAPP_NUMBER, fmessage, False, None)
    else:
      # it's a serie
      # overview, poster, trailer, media_link
      tmdb_details = get_tmdb_details(media_type, tmdb, language=LANGUAGE)
      title = tmdb_details.get('name', '')
      overview = tmdb_details.get('overview', '')
      poster_id = tmdb_details.get('poster_path', '')
      poster_path = download_and_get_poster_by_id(poster_id)
      trailer = get_trailer_link(media_type, tmdb)
      # imdb + tdmb for media_link
      imdb_link = f"• IMDb: https://imdb.com/title/{imdb}"
      # if tmdb empty, imdb to tmdb, else tmdb
      if tmdb == "":
          tmdb_link = f"• TMDb: {imdb_to_tmdb(imdb)}"
      else:
          tmdb_link = f"• TMDb: https://tmdb.org/{media_type}/{tmdb}"
      media_link = imdb_link + "\n" + tmdb_link
      # send message    
      fmessage = format_message(title, overview, media_link, trailer)
      send_whatsapp(WHATSAPP_NUMBER, fmessage, True, poster_path)

  if poster_path:
    os.remove(poster_path)

  return jsonify({'message': 'Data received successfully!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7778)

