from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import telegram
import json
import os

# Initialize bot with your token
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Or just hardcode it for now
# bot = telegram.Bot(token=TELEGRAM_TOKEN)

# @csrf_exempt
# @api_view(['POST'])
# def telegram_webhook(request):
#     data = json.loads(request.body)
#     chat_id = data['message']['chat']['id']
#     text = data['message'].get('text', '')

#     if text == '/start':
#         bot.send_message(chat_id=chat_id, text="Hello from Django Bot!")

#     return Response({"status": "ok"})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        print("✅ Webhook hit!")
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid request"}, status=400)
