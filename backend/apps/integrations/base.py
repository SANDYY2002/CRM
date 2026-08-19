from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class NormalizedInboundMessage:
    external_message_id: str
    external_user_id: str
    display_name: str
    avatar_url: str = ""
    text: str = ""
    message_type: str = "text"
    raw: dict[str, Any] | None = None


class ChannelAdapter(Protocol):
    def send_text(self, recipient_id: str, text: str) -> str: ...
    def normalize_webhook(self, payload: dict[str, Any]) -> list[NormalizedInboundMessage]: ...
