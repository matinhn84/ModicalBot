import requests
from .ai_model import build_prompt, query
from django.http import JsonResponse
def get_music_metadata(song_name):


    url = "https://shazam.p.rapidapi.com/search"

    querystring = {"term":song_name,
                   "locale":"en-US",
                   "offset":"0",
                   "limit":"5"
    }

    headers = {
        "x-rapidapi-key": "7710fb387dmshac7444e0db327b5p145deejsn0bc57da0badb",
        "x-rapidapi-host": "shazam.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    try:
        data = response.json()
        if not data.get("tracks") or not data["tracks"].get("hits"):
            return {
                "error": "No tracks found for the query.",
                "details": f"No results for: {song_name}"
            }
        else:
            first_track = data["tracks"]["hits"][0]["track"]

        result = {
            "title": first_track.get("title"),
            "artist": first_track.get("subtitle"),
            "coverart": first_track["images"].get("coverarthq"),
            "mp3": None,
            "apple_music": None,
            "spotify": None,
            "youtube_music": None,
            "soundcloud": None
        }

  
        for action in first_track.get("hub", {}).get("actions", []):
            if action.get("type") == "uri" and "itunes.apple.com" in action.get("uri"):
                result["mp3"] = action["uri"]


        for provider in first_track.get("hub", {}).get("providers", []):
            caption = provider.get("caption", "").lower()
            uri = provider.get("actions", [{}])[0].get("uri")

            if "spotify" in caption:
                result["spotify"] = uri
            elif "deezer" in caption:
                result["youtube_music"] = uri
            elif "soundcloud" in caption:
                result["soundcloud"] = uri


        for option in first_track.get("hub", {}).get("options", []):
            if option.get("caption") == "OPEN":
                result["apple_music"] = option["actions"][0].get("uri")



        

        return result

    except Exception as e:
        return {'error': 'error parsing API response', 'details': str(e)}