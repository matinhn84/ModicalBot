from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_photo_with_button
from .services.ai_model import query, build_prompt
from .services.shazam_api import get_music_metadata



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
        
        if not generated:
            raise ValueError("Empty AI result!")


        
        send_telegram_message(chat_id, generated)

        # song_meta_data = get_music_metadata(generated) # comment using func
        import requests
        url = "https://shazam.p.rapidapi.com/search"

        querystring = {"term":generated,
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
                    "details": f"No results for: {generated}"
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
            result = {'error': 'error parsing API response', 'details': str(e)}
            if 'error' in result:
                send_telegram_message(chat_id, "Eror in geting song data")
                return JsonResponse(result)

        # buttons = []
        # row = []
        # print(song_meta_data.items())
        # for name, url in song_meta_data.items():
        #     if url:
        #         row.append({"text": name.capitalize(), "url": url})
        #         if len(row)==2:
        #             buttons.append(row)
        #             row = []
        # if row:
        #     buttons.append(row)
            
        # send_photo_with_button(
        # chat_id=chat_id,
        # image_url=song_meta_data.get("coverart", ""),
        # caption=f"<b>{song_meta_data.get('title', '')}</b> — <i>{song_meta_data.get('artist', '')}</i>\n<a href='https://t.me/MoodicalBot'>Moodical  | مودیکال </a>",
        # buttons= buttons
        # )
        buttons = []
        row = []
        
        for name, url in result.items():
            if url:
                row.append({"text": name.capitalize(), "url": url})
                if len(row)==2:
                    buttons.append(row)
                    row = []
        if row:
            buttons.append(row)
            
        send_photo_with_button(
        chat_id=chat_id,
        image_url=result.get("coverart", ""),
        caption=f"<b>{result.get('title', '')}</b> — <i>{result.get('artist', '')}</i>\n<a href='https://t.me/MoodicalBot'>Moodical  | مودیکال </a>",
        buttons= buttons
        )


    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return JsonResponse({'error:':  repr(e)})
    

    finally:
        delete_telegram_message(chat_id, message_id)

    return JsonResponse({"status": 'ok'})