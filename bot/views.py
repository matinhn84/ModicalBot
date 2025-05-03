from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message, send_telegram_inline_keyboard
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
            
        buttons = [
            [{"text": "Is strong", "url": "https://tralalero-tralala.com"}],
            [{"text": "Is Weak" , "callback_data": "test_action"}]
        ]

        send_telegram_inline_keyboard(
            chat_id=123456789,
            text="Tralalero tralala",
            buttons=buttons,
            parse_mode="HTML"
)


    except Exception as e:
        print("AI error:", repr(e))
        send_telegram_message(chat_id, "Sorry! Can't find any music.")
        return JsonResponse({'error:':  repr(e)})
    

    finally:
        delete_telegram_message(chat_id, message_id)

    return JsonResponse({"status": 'ok'})