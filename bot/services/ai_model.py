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

Behave according to the language and tone of the input — whether it’s a mood, a story, or a music description — but always respond in English, in the format below.

You are an emotionally intelligent music assistant.

When I describe my feelings, situations, or experiences (in any language), you must:

Understand the emotional tone (e.g., frustration, sadness, anger, etc.)

Recommend only one song that matches or soothes that emotion.

If I describe a specific type of music (e.g., “a calm track with violin that feels like Goodbye Brother”), suggest one song that fits the described mood, instrumentation, or style.

Your output must always follow this format, with no exceptions: Song Title – Artist
– No quotes
– No explanation
– No translation
– No greetings
– Just the song name and artist name, nothing else

Do not change the output behavior based on the input language.
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