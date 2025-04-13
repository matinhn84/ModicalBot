# downloader/views.py
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from youtubesearchpython import VideosSearch
import yt_dlp
from django.http import FileResponse
import os

class DownloadMusicView(APIView):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query is required."}, status=400)

        search = VideosSearch(query, limit=1)
        result = search.result()["result"]
        if not result:
            return Response({"error": "No result found."}, status=404)
        video_url = result[0]["link"]
        title = result[0]["title"]

        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_path = temp_file.name
            temp_file.close()

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_path,
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'},
                    {'key': 'EmbedThumbnail'},
                    {'key': 'FFmpegMetadata'},
                ],
                'writethumbnail': True,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            response = FileResponse(open(temp_path, 'rb'), as_attachment=True, filename=f"{title}.mp3")
            response['X-Accel-Buffering'] = 'no'
            response['Content-Disposition'] = f'attachment; filename="{title}.mp3"'
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
