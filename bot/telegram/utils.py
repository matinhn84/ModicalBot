import requests

TOKEN = '7687944134:AAExhPl0bOBKI2ID_qsi4fzEDVDhOW5urLw'

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        print("Telegram API error:", response.status_code, response.text)
        return None

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



def send_photo_with_button(chat_id, image_url, caption, buttons):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": buttons
        }
    }

    return requests.post(url, json=payload)