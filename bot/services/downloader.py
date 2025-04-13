from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import yt_dlp
import tempfile
import os

class DownloadMusicView(APIView):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Missing 'query' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # جستجوی ویدیو از طریق yt-dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                if not info['entries']:
                    return Response({"error": "No results found."}, status=status.HTTP_404_NOT_FOUND)
                video = info['entries'][0]
                video_url = video['webpage_url']
                title = video['title']
        except Exception as e:
            return Response({"error": f"Search failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_path,
                'quiet': True,
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'},
                    {'key': 'EmbedThumbnail'},
                    {'key': 'FFmpegMetadata'},
                ],
                'writethumbnail': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            response = FileResponse(open(temp_path, 'rb'), as_attachment=True, filename=f"{title}.mp3")
            response['X-Accel-Buffering'] = 'no'
            return response

        except Exception as e:
            return Response({"error": f"Download failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
