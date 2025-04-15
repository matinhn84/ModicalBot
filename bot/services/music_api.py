# views/music_api.py
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_song_info(query):

    search_res = requests.get(f"https://saavn.dev/api/search?query={query}")
    songs = search_res.json().get('data', {}).get('songs', {}).get('results', [])
    if not songs:
        return Response({'error': 'No songs found'}, status=404)

    song = songs[0]
    song_id = song.get('id')
    title = song.get('title')
    artist = song.get('primaryArtists')
    thumbnail = next((img.get("url") for img in song.get("image", []) if img.get("quality") == "150x150"), None)

    # Get MP3 link
    song_detail_res = requests.get(f"https://saavn.dev/api/songs?id={song_id}")
    song_data = song_detail_res.json().get('data', [])[0]
    mp3_link = next((x['link'] for x in song_data['downloadUrl'] if x['quality'] == '320kbps'), None)

    return Response({
        'title': title,
        'artist': artist,
        'thumbnail': thumbnail,
        'mp3': mp3_link
    })


