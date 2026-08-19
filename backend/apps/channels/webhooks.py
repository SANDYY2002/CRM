import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .adapters import get_adapter
from .models import Channel
from .services import ingest_normalized_message


@csrf_exempt
def channel_webhook(request, channel_id: int):
    if request.method not in ("POST", "GET"):
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        channel = Channel.objects.get(pk=channel_id, is_active=True)
    except Channel.DoesNotExist:
        return JsonResponse({"detail": "Channel not found."}, status=404)

    adapter = get_adapter(channel.type, channel.credentials)

    if request.method == "GET":
        return JsonResponse({"status": "ready", "channel": channel.type})

    if not adapter.verify_webhook(dict(request.headers), request.body):
        return JsonResponse({"detail": "Webhook verification failed."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"detail": "Invalid JSON."}, status=400)

    events = adapter.parse_webhook(payload)
    created = []
    for event in events:
        message = ingest_normalized_message(channel, event)
        created.append(message.id)

    return JsonResponse({"status": "accepted", "message_ids": created})
