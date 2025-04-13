from django.urls import path
from .views import telegram_webhook
from .services.downloader import DownloadMusicView
urlpatterns = [
    path('webhook/', telegram_webhook, name='telegram_webhook'),
    path("download/", DownloadMusicView.as_view(), name="download-music"),
]
