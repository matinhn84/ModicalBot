import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

TOKEN = '7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw'
HF_URL = 'https://api.telegram.org/bot{TOKEN}/ai/song/'

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # send view to hugging face
        response = requests.post(HF_URL, json={"message": text})
        ai_response = response.json()


        ai_response = query({
            "inputs": build_prompt(text) #*************
        })

        if text=="/start":
            response_text = "Hi! The bot lets you to access the best music\
                according to your mood!Let\'s start, type your current mood."
        else:
            response_text = ai_response[0]["generated_text"]\
                 if isinstance(ai_response, list)\
                     else "Sorry! can\'t understand!🤔"

        # response
        send_telegram_message(chat_id, response_text)

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid request"}, status=400)


def send_telegram_message(chat_id, text):
    TELEGRAM_TOKEN = "7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# Use Cerebras API

HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@csrf_exempt
def song_recommendation(request):
    if request.method == "POST":
        body = json.loads(request.body)
        user_input = body.get("message", "")
     

        result = query({
            "inputs": user_input
        })

        return JsonResponse(result, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)


def build_prompt(user_input):
    return f"""
You are an AI that suggests songs based on the user's mood.
User's mood: "I feel lonely and nostalgic"

{user_input}

Only return in this format:
Song: [song name]
Artist: [artist name]

"""
