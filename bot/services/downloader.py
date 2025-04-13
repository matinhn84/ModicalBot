# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from youtubesearchpython import VideosSearch
import yt_dlp
import tempfile
import os


class DownloadMusicView(APIView):
    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Missing 'query' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        # جستجوی ویدیو در یوتیوب
        try:
            search = VideosSearch(query, limit=1)
            result = search.result()["result"]
            if not result:
                return Response({"error": "No results found."}, status=status.HTTP_404_NOT_FOUND)

            video_url = result[0]["link"]
            title = result[0]["title"]
        except Exception as e:
            return Response({"error": f"YouTube search failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # دانلود آهنگ در فایل موقتی
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

            # ارسال فایل به صورت پاسخ
            response = FileResponse(open(temp_path, 'rb'), as_attachment=True, filename=f"{title}.mp3")
            response['X-Accel-Buffering'] = 'no'
            return response

        except Exception as e:
            return Response({"error": f"Download failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
