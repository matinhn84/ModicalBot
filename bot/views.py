import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

TOKEN = '7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw'

HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/cerebras/Cerebras-GPT-2.7B"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def build_prompt(user_input):
    return f"""
You are an AI that suggests songs based on the user's mood.
User's mood: "{user_input}"

Only return in this format:
Song: [song name]
Artist: [artist name]

Do not include anything else.
"""

def query(prompt):
    data = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()[0]['generated_text']

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        if text == "/start":
            response_text = "Hi! This bot recommends music based on your mood. 🎵\nTell me how you feel right now."
        else:
            prompt = build_prompt(text)
            try:
                response_text = query(prompt)
            except Exception as e:
                response_text = "Oops! Something went wrong talking to the AI model. 🛠"

        send_telegram_message(chat_id, response_text)
        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid request"}, status=400)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@csrf_exempt
def song_recommendation(request):
    if request.method == "POST":
        body = json.loads(request.body)
        user_input = body.get("message", "")
        prompt = build_prompt(user_input)
        try:
            result = query(prompt)
            return JsonResponse({"result": result})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
