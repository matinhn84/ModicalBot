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


        if chat_id:
            if text == "/start":
                message = 'Hi! The bot lets you to access the best music according to your mood!Let\'s start, type your current mood.'
            else:
                if isinstance(ai_response, list):
                    message = ai_response[0]["generated_text"]
                else:
                    message = "Sorry cant understand!"
            
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
                'chat_id' : chat_id,
                'text' : message
            })

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid request"}, status=400)



# Use Cerebras API

HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/cerebras/btlm-3b-8k-base"

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
