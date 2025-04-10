import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

TOKEN = '7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw'

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("تلگرام گفت:", data)

        chat_id = data.get("message", {}).get("chat", {}).get("id")
        text = data.get("message", {}).get("text")

        if chat_id:
            if text == "/start":
                message = 'Hi! The bot lets you to access the best music according to your mood!Let\'s start, type your current mood.'
            else:
                message = f'You said: {text}'
            
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
                'chat_id' : chat_id,
                'text' : message
            })

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid request"}, status=400)
