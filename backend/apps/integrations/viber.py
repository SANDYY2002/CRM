import hashlib
import hmac
from typing import Any

import requests

from .base import NormalizedInboundMessage


class ViberAdapter:
    API_URL = "https://chatapi.viber.com/pa"

    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    def _headers(self) -> dict[str, str]:
        return {"X-Viber-Auth-Token": self.auth_token, "Content-Type": "application/json"}

    def set_webhook(self, webhook_url: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.API_URL}/set_webhook",
            json={"url": webhook_url, "send_name": True, "send_photo": True},
            headers=self._headers(), timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def send_text(self, recipient_id: str, text: str) -> str:
        response = requests.post(
            f"{self.API_URL}/send_message",
            json={"receiver": recipient_id, "type": "text", "text": text},
            headers=self._headers(), timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") != 0:
            raise RuntimeError(data.get("status_message", "Viber send failed"))
        return str(data.get("message_token", ""))

    def verify_signature(self, raw_body: bytes, signature: str) -> bool:
        expected = hmac.new(self.auth_token.encode(), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def normalize_webhook(self, payload: dict[str, Any]) -> list[NormalizedInboundMessage]:
        if payload.get("event") != "message":
            return []
        sender = payload.get("sender") or {}
        message = payload.get("message") or {}
        user_id = str(sender.get("id", ""))
        message_token = str(payload.get("message_token", ""))
        if not user_id or not message_token:
            return []
        return [NormalizedInboundMessage(
            external_message_id=message_token,
            external_user_id=user_id,
            display_name=sender.get("name") or "Viber user",
            avatar_url=sender.get("avatar") or "",
            text=message.get("text") or "",
            message_type=message.get("type") or "text",
            raw=payload,
        )]
