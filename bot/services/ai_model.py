import requests

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
"{user_input}"

The text above — without according to it's lanquage, whether it's a mood, a story, or a music description — and respond accordingly.
You are an emotionally intelligent music assistant.
When I describe my feelings, situations, or experiences (e.g., "I was stuck in traffic and got fired today"), you must:
Understand the emotional tone (e.g., frustration, sadness, anger, etc.)
Recommend just one song that match or soothe that emotion
The song you recommend can be in any lanquage and You do not need to match the language of the music to the language I use.
If I describe a specific type of music (e.g., “a calm track with violin that feels like Goodbye Brother”), suggest songs that are similar in mood, instrumentation, or style
I don't need to your explanation!
Always recommend music using this exact format: music title – artist.(Don't put the song title in qoutes)
Don't add any explanation at all!.
"""
# replace at "least 5" to "just" for test

# def build_prompt(user_input):
#     return f"""
# "{user_input}"

# The text above — whether it's a mood, a story, or a music description — and respond accordingly.
# Respond using the same language I use in my message, except for the song titles which should always be in English
# You are an emotionally intelligent music assistant.
# When I describe my feelings, situations, or experiences (e.g., "I was stuck in traffic and got fired today"), you must:
# Understand the emotional tone (e.g., frustration, sadness, anger, etc.)
# Recommend just songs that match or soothe that emotion
# You do not need to match the language of the music to the language I use
# If I describe a specific type of music (e.g., “a calm track with violin that feels like Goodbye Brother”), suggest songs that are similar in mood, instrumentation, or style
# Always list songs using this exact format: [music title] – [artist]
# Keep your replies short and focused on the music — avoid long explanations unless I explicitly ask

# """