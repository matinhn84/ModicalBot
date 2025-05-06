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
        pure_song_name = str(generated).splitlines()[0]

        
        if not generated:
            raise ValueError("Empty AI result!")


        
        send_telegram_message(chat_id, generated)

        music_data = get_music_metadata(pure_song_name)

        buttons = []
        row = []
        button_keys = ["mp3", "apple_music", "spotify", "youtube_music", "soundcloud"]
        for key in button_keys:
            url = music_data.get(key)
            if url:
                row.append({"text": key, "url": url})
                if len(row) == 2:
                    buttons.append(row)
                    row = []
        if row:
            buttons.append(row)
        print(buttons)

 
        send_photo_with_button(
        chat_id=chat_id,
        image_url=music_data.get("coverart"),
        caption=f"<b>{music_data.get('title')}</b> — <i>{music_data.get('artist')}</i>\n<a href='https://t.me/MoodicalBot'>Moodical  | مودیکال </a>",
        buttons= buttons
        )


    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return JsonResponse({'error:':  repr(e)})
    

    finally:
        if message_id:
            delete_telegram_message(chat_id, message_id)
        print('done'.join('**'))

    return JsonResponse({"status": 'ok'})


