from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print("📩 Webhook received:", data)
        return JsonResponse({'status': 'received'})
    return JsonResponse({'error': 'invalid request'}, status=400)
