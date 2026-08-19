from typing import Any

from .base import NormalizedMessage


class BaseAdapter:
    channel_type = "unknown"

    def __init__(self, credentials: dict[str, Any] | None = None):
        self.credentials = credentials or {}

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]:
        raise NotImplementedError

    def send_message(self, external_customer_id: str, content: str) -> dict[str, Any]:
        raise NotImplementedError

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        return False


class FacebookAdapter(BaseAdapter):
    channel_type = "facebook"


class InstagramAdapter(BaseAdapter):
    channel_type = "instagram"


class WhatsAppAdapter(BaseAdapter):
    channel_type = "whatsapp"


class ViberAdapter(BaseAdapter):
    channel_type = "viber"


class YouTubeAdapter(BaseAdapter):
    channel_type = "youtube"


ADAPTERS = {
    FacebookAdapter.channel_type: FacebookAdapter,
    InstagramAdapter.channel_type: InstagramAdapter,
    WhatsAppAdapter.channel_type: WhatsAppAdapter,
    ViberAdapter.channel_type: ViberAdapter,
    YouTubeAdapter.channel_type: YouTubeAdapter,
}


def get_adapter(channel_type: str, credentials: dict[str, Any] | None = None) -> BaseAdapter:
    try:
        adapter_class = ADAPTERS[channel_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported channel type: {channel_type}") from exc
    return adapter_class(credentials)
