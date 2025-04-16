# services/music_api.py
import requests

from rest_framework.response import Response


def get_song_info(query):
    try:
        search_res = requests.get(f"https://saavn.dev/api/search?query={query}")
        if not search_res.ok:
            return Response({'error': 'No songs returned'}, status=404)
        songs = search_res.json().get('data', {}).get('songs', {}).get('results', [])
        if not songs:
            return Response({'error': 'No songs found'}, status=404)

        song = songs[0]
        song_id = song.get('id')
        title = song.get('title')
        artist = song.get('primaryArtists')
        thumbnail = next((img.get("url") for img in song.get("image", []) if img.get("quality") == "150x150"), None)

        # Get MP3 link
        song_detail_res = requests.get(f"https://saavn.dev/api/search/songs?query={song_id}")
        song_data = song_detail_res.json().get('data', []).get('results', [])

        download_urls = song_data[0].get('downloadUrl', [])
        mp3_link = next((x['url'] for x in download_urls if x.get('quality') == '320kbps'), None)
        if not mp3_link:
            return Response({'error': 'No mp3 link for this song!'}, status=404)

        return Response({
            'title': title,
            'artist': artist,
            'thumbnail': thumbnail,
            'mp3': mp3_link
        })
    except Exception as e:
        print('error:', e)


