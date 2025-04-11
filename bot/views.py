import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

TOKEN = '7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw'


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)

        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # send view to hugging face


        if text=="/start":
            response_text = "Hi! The bot lets you to access the best music\
                according to your mood!Let\'s start, type your current mood."
        else:
            prompt = build_prompt(text)
            try:
                ai_response = query({
                    "inputs": prompt
                })

                if isinstance(ai_response, list) and "generated_text" in ai_response[0]:
                    generated = ai_response[0]["generated_text"]

                    # حذف prompt از ابتدای خروجی
                    if generated.startswith(prompt):
                        generated = generated[len(prompt):].strip()

                    response_text = generated if generated else "Sorry! couldn't generate a song 🎵"
                else:
                    response_text = "Sorry! can't understand!🤔"

            except Exception as e:
                print("AI error:", e)
                response_text = "Something went wrong with AI model! 😔"
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



def build_prompt(user_input):
    return f"""
You are an AI that suggests songs based on the user's mood.
User's mood: "I feel lonely and nostalgic"

"{user_input}"

Only return in this format:
Song: [song name]
Artist: [artist name]

"""
