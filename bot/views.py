

# @csrf_exempt
# def telegram_webhook(request):
#     if request.method == 'POST':
#         data = json.loads(request.body.decode('utf-8'))
#         print("📩 Webhook received:", data)
#         return JsonResponse({'status': 'received'})
#     return JsonResponse({'error': 'invalid request'}, status=400)

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

        if chat_id and text:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
                "chat_id": chat_id,
                "text": "تو گفتی: " + text
            })

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid request"}, status=400)
