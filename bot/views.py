from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_photo_with_button
from .services.ai_model import query, build_prompt



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
            
        send_photo_with_button(
        chat_id=chat_id,
        image_url="https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/20/75/39/207539da-60d1-8ac1-7f4f-9f7e534c8c85/00030206709728.rgb.jpg/400x400cc.jpg",
        caption="<b>Moments (Super Slowed + Reverb)</b> — <i>danjerr</i>\n<a href='https://t.me/yourchannel'>Music Finder | موزیک یاب</a>",
        button_text="Google",
        button_url="https://google.com"
)


    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return JsonResponse({'error:':  repr(e)})
    

    finally:
        delete_telegram_message(chat_id, message_id)

    return JsonResponse({"status": 'ok'})