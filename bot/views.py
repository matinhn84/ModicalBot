from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_telegram_audio
from .services.ai_model import query, build_prompt
from .services.music_api import get_song_info

@csrf_exempt
def telegram_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "invalid request"}, status=400)

    data = json.loads(request.body)
    print(data)

    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    processing_msg  = send_telegram_message(chat_id, "Processing...")
    message_id = processing_msg["result"]["message_id"]

    if text == "/start":
        response_text = "Hi! The bot lets you access the best music according to your mood!\nType your current mood."
    else:
        prompt = build_prompt(text)
    try:
        ai_response = query(prompt)
        generated = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not generated:
            raise ValueError("Empty AI result!")

        song_info = get_song_info(generated)

        if isinstance(song_info, dict):
            mp3 = song_info['mp3']
            title = song_info['title']
            performer = song_info['artist']
            thumb = song_info['thumbnail']

            send_telegram_audio(chat_id, mp3, title, performer, thumb)

        else:
            raise ValueError("song_info is not valid dict")

    except Exception as e:
        import traceback
        print("AI error:", repr(e))
        traceback.print_exc()
        send_telegram_message(chat_id, "Something went wrong!")


    return JsonResponse({"status": "ok"})
