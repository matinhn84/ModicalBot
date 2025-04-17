from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_telegram_audio
from .services.ai_model import query, build_prompt
from .services.music_api import get_song_info

from django.http import HttpResponse
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

        if not generated:
            raise ValueError("Empty AI result!")

        # song_info = get_song_info(generated)
        # if not song_info or not isinstance(song_info, dict):
        #     raise ValueError("Song info fetch failed")
        # **
        try:
            search_res = requests.get(f"https://saavn.dev/api/search?query={generated}")
            if not search_res.ok:
                print("Search failed:", search_res.status_code)
                return None

            data = search_res.json()
            top_result = data.get('data', {}).get('songs', {}).get('results')

            if not top_result:
                print("No topQuery results found")
                return None

            song = top_result[0]
            title = song.get('title')
            artist = song.get('primaryArtists', '')
            thumbnail = next((img.get("url") for img in song.get("image", []) if img.get("quality") == "150x150"), None)

            # Get MP3
            song_detail_res = requests.get(f"https://saavn.dev/api/search/songs?query={title}")
            if not song_detail_res.ok:
                print("Details fetch failed")
                return None

            song_data = song_detail_res.json()
            results = song_data.get('data', {}).get('results', [])

            # if not results:
            #     print("No detailed results")
            #     return None

            download_urls = results[0].get('downloadUrl', [])
            mp3_link = next((x['url'] for x in download_urls if x.get('quality') == '320kbps'), None)



        except Exception as e:
            print("get_song_info error:", repr(e))

        send_telegram_audio(chat_id, mp3_link, title, artist, thumbnail)
        # **

        # mp3 = song_info.get('mp3')
        # title = song_info.get('title')
        # performer = song_info.get('artist')
        # thumb = song_info.get('thumbnail')

        # if not all([mp3, title]):
        #     raise ValueError("Incomplete song data")

        # send_telegram_audio(chat_id, mp3, title, performer, thumb)

    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return HttpResponse("Internal Server Error", status=500)

    finally:
        delete_telegram_message(chat_id, message_id)

    return JsonResponse({"status": mp3_link})