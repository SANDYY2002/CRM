from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.channels.models import Channel
from apps.conversations.models import Conversation, Message
from apps.customers.models import Customer
from .adapters.base import NormalizedMessage


@transaction.atomic
def ingest_normalized_message(channel: Channel, event: NormalizedMessage) -> Message:
    customer = Customer.objects.filter(
        organization=channel.organization,
        metadata__external_ids__contains={channel.type: event.external_customer_id},
    ).first()

    if customer is None:
        customer = Customer.objects.create(
            organization=channel.organization,
            first_name=event.customer_name or event.external_customer_id,
            email=event.customer_email,
            phone=event.customer_phone,
            metadata={"external_ids": {channel.type: event.external_customer_id}},
        )

    conversation, _ = Conversation.objects.get_or_create(
        organization=channel.organization,
        customer=customer,
        channel=channel,
        defaults={"status": Conversation.Status.OPEN},
    )

    message, created = Message.objects.get_or_create(
        conversation=conversation,
        external_id=event.external_message_id,
        defaults={
            "direction": event.direction,
            "message_type": event.message_type,
            "content": event.content,
            "metadata": event.metadata,
            "is_read": False,
            "created_at": parse_datetime(event.sent_at) if event.sent_at else None,
        },
    )

    if created:
        conversation.unread_count = conversation.unread_count + 1 if event.direction == Message.Direction.INBOUND else conversation.unread_count
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=["unread_count", "last_message_at", "updated_at"])

    return message
