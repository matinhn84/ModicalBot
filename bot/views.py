from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .telegram.utils import send_telegram_message, delete_telegram_message
from .services.ai_model import query, build_prompt

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
            response_text = generated or "Sorry! Couldn't generate a song 🎵"
        except Exception as e:
            print("AI error:", e)
            response_text = "Something went wrong with AI model! 😔"

    delete_telegram_message(chat_id, message_id)
    send_telegram_message(chat_id, response_text)

    return JsonResponse({"status": "ok"})
