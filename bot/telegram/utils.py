import requests

TOKEN = '7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw'

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

def delete_telegram_message(chat_id, message_id):
    url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    requests.post(url, json=payload)


def send_telegram_audio(chat_id, mp3_link, title, artist, thumb_url):
    url = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
    payload = {
        'chat_id': chat_id,
        'audio': mp3_link,
        'title': title,
        'performer': artist,
        'thumb': thumb_url or ""
    }
    requests.post(url, json=payload)