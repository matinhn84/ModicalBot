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
                ai_response = query(prompt)
                print(f"*****{ai_response}*****")

                if "choices" in ai_response and len(ai_response["choices"]) > 0:
                    generated = ai_response["choices"][0]["message"]["content"]

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
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# Use Cerebras API

HF_TOKEN = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://yourproject.com"
}

def query(user_prompt):
    payload = {
        "model": "google/gemini-pro",
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()  
    return response.json()




def build_prompt(user_input):
    return f"""
You are an emotionally intelligent music assistant. When I describe my feelings, situations, or experiences (e.g., "I was stuck in traffic and got fired today"), you must understand the emotional tone (e.g., frustration, sadness, anger) and recommend at least 5 songs that match or help soothe that emotional state.

You do not need to match the language of the music to the language I use.

If I describe a specific kind of music I'm looking for (e.g., “a calm track with violin that feels like Goodbye Brother”), suggest songs that are similar in mood, instrumentation, or style.

Always provide song recommendations in the following format: [music title] – [artist]

Respond to me in the same language I use in my prompt, except for the song titles.

Do not add explanations unless I ask for them.

main prompt:
"{user_input}"

"""
