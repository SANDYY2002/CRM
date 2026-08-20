from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.channels.adapters.providers import get_adapter
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


@receiver(post_save, sender=Message)
def deliver_outbound_message(sender, instance: Message, created: bool, **kwargs):
    if not created or instance.direction != Message.Direction.OUTBOUND or instance.external_id:
        return
    if not instance.content.strip() or instance.conversation.channel.type == Channel.Types.YOUTUBE:
        return

    conversation = instance.conversation
    external_ids = (conversation.customer.metadata or {}).get("external_ids") or {}
    external_customer_id = external_ids.get(conversation.channel.type)
    if not external_customer_id:
        instance.metadata = {**instance.metadata, "delivery_status": "not_sent", "delivery_error": "Customer has no provider external ID."}
        Message.objects.filter(pk=instance.pk).update(metadata=instance.metadata)
        return

    try:
        result = get_adapter(conversation.channel.type, conversation.channel.credentials).send_message(
            str(external_customer_id), instance.content
        )
        external_id = str(result.get("external_message_id") or "")
        metadata = {**instance.metadata, "delivery_status": "sent", "provider_response": result.get("raw", {})}
        Message.objects.filter(pk=instance.pk).update(external_id=external_id, metadata=metadata)
    except Exception as exc:  # provider failures must remain visible in the CRM
        metadata = {**instance.metadata, "delivery_status": "failed", "delivery_error": str(exc)}
        Message.objects.filter(pk=instance.pk).update(metadata=metadata)
