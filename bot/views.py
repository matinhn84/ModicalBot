from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_telegram_audio
from .services.ai_model import query, build_prompt
from .services.music_api import get_song_info

from django.http import HttpResponse

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

        song_info = get_song_info(generated)
        if not song_info or not isinstance(song_info, dict):
            raise ValueError("Song info fetch failed")

        mp3 = song_info.get('mp3')
        title = song_info.get('title')
        performer = song_info.get('artist')
        thumb = song_info.get('thumbnail')

        if not all([mp3, title]):
            raise ValueError("Incomplete song data")

        send_telegram_audio(chat_id, mp3, title, performer, thumb)

    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return HttpResponse("Internal Server Error", status=500)

    finally:
        delete_telegram_message(chat_id, message_id)

    return JsonResponse({"status": 'ok'})@csrf_exempt
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

        song_info = get_song_info(generated)
        if not song_info or not isinstance(song_info, dict):
            raise ValueError("Song info fetch failed")

        mp3 = song_info.get('mp3')
        title = song_info.get('title')
        performer = song_info.get('artist')
        thumb = song_info.get('thumbnail')

        if not all([mp3, title]):
            raise ValueError("Incomplete song data")

        send_telegram_audio(chat_id, mp3, title, performer, thumb)

    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return HttpResponse("Internal Server Error", status=500)

    finally:
        delete_telegram_message(chat_id, message_id)

    return JsonResponse({"status": 'ok'})