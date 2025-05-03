from django.urls import path
from .views import telegram_webhook
from .services.shazam_api import get_music_metadata 
urlpatterns = [
    path('webhook/', telegram_webhook, name='telegram_webhook'),
    path('shazam/', get_music_metadata, name='get_music_metadata'),
]
