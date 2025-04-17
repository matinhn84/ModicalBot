# services/music_api.py
import requests

from rest_framework.response import Response
from django.http import JsonResponse

def get_song_info(query):
    try:
        search_res = requests.get(f"https://saavn.dev/api/search?query={query}")
        if not search_res.ok():
            return 'error: search_res'
        data = search_res.json()

        song = data['data']['topQuery']['results'][0]
        title = song['title']
        artist = song['primaryArtists']
        thumbnail = next((img.get("url") for img in song.get("image", []) if img.get("quality") == "150x150"), None)

        # Get MP3 link
        song_detail_res = requests.get(f"https://saavn.dev/api/search/songs?query={title}")
        song_data = song_detail_res.json()

        download_urls = song_data['data']['results'][0]['downloadUrl']
        mp3_link = next((x['url'] for x in download_urls if x.get('quality') == '320kbps'), None)


        return Response({
            'title': title,
            'artist': artist,
            'thumbnail': thumbnail,
            'mp3': mp3_link
        })
    except Exception as e:
        return JsonResponse({'error': e})


