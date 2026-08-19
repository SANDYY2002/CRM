from django.conf import settings
from django.db import models
from apps.channels.models import Channel
from apps.customers.models import Customer
from apps.organizations.models import Organization


class Conversation(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        PENDING = "pending", "Pending"
        CLOSED = "closed", "Closed"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="conversations")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="conversations")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="conversations")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    unread_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_message_at", "-updated_at"]


class Message(models.Model):
    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"
        INTERNAL = "internal", "Internal"

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        FILE = "file", "File"
        AUDIO = "audio", "Audio"
        SYSTEM = "system", "System"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="sent_messages")
    external_id = models.CharField(max_length=255, blank=True)
    direction = models.CharField(max_length=20, choices=Direction.choices)
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField(blank=True)
    attachment_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["external_id"]),
        ]
