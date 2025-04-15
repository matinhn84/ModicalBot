from django.urls import path
from .views import telegram_webhook
from .services.music_api import search_music
urlpatterns = [
    path('webhook/', telegram_webhook, name='telegram_webhook'),
    path("search_music/", search_music, name="download-music"),
]
