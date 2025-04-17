# services/music_api.py
import requests

from rest_framework.response import Response
from django.http import JsonResponse

def get_song_info(query):
    try:
        search_res = requests.get(f"https://saavn.dev/api/search?query=goodbye brother")
        if not search_res.ok:
            print("Search failed:", search_res.status_code)
            return None

        data = search_res.json()
        top_result = data.get('data', {}).get('topQuery', {}).get('results', [])

        if not top_result:
            print("No topQuery results found")
            return None

        song = top_result[0]
        title = song.get('title')
        artist = song.get('primaryArtists', '')
        thumbnail = next((img.get("url") for img in song.get("image", []) if img.get("quality") == "150x150"), None)

        # Get MP3
        song_detail_res = requests.get(f"https://saavn.dev/api/search/songs?query={title}")
        if not song_detail_res.ok:
            print("Details fetch failed")
            return None

        song_data = song_detail_res.json()
        results = song_data.get('data', {}).get('results', [])

        if not results:
            print("No detailed results")
            return None

        download_urls = results[0].get('downloadUrl', [])
        mp3_link = next((x['url'] for x in download_urls if x.get('quality') == '320kbps'), None)

        return {
            'title': title,
            'artist': artist,
            'thumbnail': thumbnail,
            'mp3': mp3_link
        }

    except Exception as e:
        print("get_song_info error:", repr(e))
        return None


