from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_photo_with_button
from .services.ai_model import query, build_prompt
from .services.shazam_api import get_music_metadata

import requests


@csrf_exempt
def telegram_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        processing_msg = send_telegram_message(chat_id, "Processing...")
        message_id = processing_msg["result"]["message_id"]

        if text == "/start":
            send_telegram_message(chat_id, "Hi! The bot lets you access the best music according to your mood!\nType your current mood.")
            delete_telegram_message(chat_id, message_id)
            return JsonResponse({"status": "start_handled"})

        prompt = build_prompt(text)
        ai_response = query(prompt)
        generated = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        pure_song_name = str(generated).splitlines()[0]

        
        if not generated:
            raise ValueError("Empty AI result!")


        
        send_telegram_message(chat_id, generated)

        # result = get_music_metadata(pure_song_name)
        url = "https://shazam.p.rapidapi.com/search"

        querystring = {"term":pure_song_name,
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
                    "details": f"No results for: {pure_song_name}"
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

        except Exception as e:
            return JsonResponse({'error': 'error parsing API response', 'details': str(e)})


        buttons = []
        row = []
        button_keys = ["mp3", "apple_music", "spotify", "youtube_music", "soundcloud"]
        for key in button_keys:
            url = result.get(key, '')  
            row.append({"text":key, "url": url})
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        print(buttons)


        image_url=result.get("coverart")
        text = f"<b>{result.get('title')}</b> — <i>{result.get('artist')}</i>\n<a href='https://t.me/MoodicalBot'>Moodical</a>"

        send_photo_with_button(chat_id,
                                image_url,
                                text,
                                [[{"text": "MP3", "url": "https://example.com/mp3"}, {"text": "Apple Music", "url": "https://example.com/apple"}],[{"text": "Spotify", "url": "https://example.com/spotify"}, {"text": "YouTube", "url": "https://example.com/youtube"}],[{"text": "SoundCloud", "url": "https://example.com/soundcloud"}]]
                               )


    except Exception as e:
        print("error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return JsonResponse({'error:':  repr(e)})
    

    finally:
        if message_id:
            delete_telegram_message(chat_id, message_id)
        print('done!'.join('**'))

    return JsonResponse({"status": 'ok'})


# ttt