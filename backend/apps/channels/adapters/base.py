from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class NormalizedMessage:
    external_message_id: str
    external_customer_id: str
    customer_name: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    content: str = ""
    message_type: str = "text"
    direction: str = "inbound"
    sent_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ChannelAdapter(Protocol):
    channel_type: str

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]: ...

    def send_message(self, external_customer_id: str, content: str) -> dict[str, Any]: ...

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool: ...
