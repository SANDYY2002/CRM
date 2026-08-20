from __future__ import annotations

import hashlib
import hmac
from typing import Any

import requests

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
        return True


class MetaAdapter(BaseAdapter):
    graph_base = "https://graph.facebook.com"
    graph_version = "v23.0"

    def _access_token(self) -> str:
        token = self.credentials.get("access_token") or self.credentials.get("token")
        if not token:
            raise RuntimeError(f"{self.channel_type}: access token is not configured")
        return str(token)

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.graph_base}/{self.graph_version}/{endpoint.lstrip('/')}"
        response = requests.post(url, params={"access_token": self._access_token()}, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def send_message(self, external_customer_id: str, content: str) -> dict[str, Any]:
        endpoint = self.credentials.get("send_endpoint")
        if not endpoint:
            raise RuntimeError(f"{self.channel_type}: send_endpoint is not configured")
        data = self._post(endpoint, {"recipient": {"id": external_customer_id}, "message": {"text": content}})
        return {"external_message_id": data.get("message_id") or data.get("id"), "raw": data}

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        app_secret = self.credentials.get("app_secret")
        signature = headers.get("X-Hub-Signature-256") or headers.get("x-hub-signature-256")
        if not app_secret or not signature:
            return False
        expected = "sha256=" + hmac.new(str(app_secret).encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def _messages_from_messaging(self, events: list[dict[str, Any]]) -> list[NormalizedMessage]:
        results: list[NormalizedMessage] = []
        for event in events:
            message = event.get("message") or {}
            sender = event.get("sender") or {}
            message_id = message.get("mid")
            customer_id = sender.get("id")
            if not message_id or not customer_id or message.get("is_echo"):
                continue
            results.append(NormalizedMessage(
                external_message_id=str(message_id),
                external_customer_id=str(customer_id),
                customer_name="Meta user",
                content=str(message.get("text") or ""),
                message_type="text",
                metadata={"provider": self.channel_type, "raw": event},
            ))
        return results


class FacebookAdapter(MetaAdapter):
    channel_type = "facebook"

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]:
        results: list[NormalizedMessage] = []
        for entry in payload.get("entry", []):
            results.extend(self._messages_from_messaging(entry.get("messaging", [])))
        return results


class InstagramAdapter(MetaAdapter):
    channel_type = "instagram"

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]:
        results: list[NormalizedMessage] = []
        for entry in payload.get("entry", []):
            results.extend(self._messages_from_messaging(entry.get("messaging", [])))
        return results


class WhatsAppAdapter(MetaAdapter):
    channel_type = "whatsapp"

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]:
        results: list[NormalizedMessage] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value") or {}
                contacts = {str(c.get("wa_id")): c for c in value.get("contacts", [])}
                for message in value.get("messages", []):
                    external_customer_id = str(message.get("from", ""))
                    message_id = str(message.get("id", ""))
                    if not external_customer_id or not message_id:
                        continue
                    contact = contacts.get(external_customer_id) or {}
                    profile = contact.get("profile") or {}
                    content = (message.get("text") or {}).get("body", "")
                    results.append(NormalizedMessage(
                        external_message_id=message_id,
                        external_customer_id=external_customer_id,
                        customer_name=profile.get("name") or external_customer_id,
                        content=content,
                        message_type=str(message.get("type") or "text"),
                        metadata={"provider": "whatsapp", "raw": message},
                    ))
        return results

    def send_message(self, external_customer_id: str, content: str) -> dict[str, Any]:
        phone_number_id = self.credentials.get("phone_number_id")
        if not phone_number_id:
            raise RuntimeError("whatsapp: phone_number_id is not configured")
        endpoint = str(self.credentials.get("send_endpoint") or f"{phone_number_id}/messages")
        return self._post(endpoint, {
            "messaging_product": "whatsapp",
            "to": external_customer_id,
            "type": "text",
            "text": {"preview_url": False, "body": content},
        })


class ViberAdapter(BaseAdapter):
    channel_type = "viber"
    api_url = "https://chatapi.viber.com/pa"

    def _token(self) -> str:
        token = self.credentials.get("auth_token") or self.credentials.get("access_token")
        if not token:
            raise RuntimeError("viber: auth_token is not configured")
        return str(token)

    def _headers(self) -> dict[str, str]:
        return {"X-Viber-Auth-Token": self._token(), "Content-Type": "application/json"}

    def verify_webhook(self, headers: dict[str, str], body: bytes) -> bool:
        signature = headers.get("X-Viber-Content-Signature") or headers.get("x-viber-content-signature")
        if not signature:
            return False
        digest = hmac.new(self._token().encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)

    def send_message(self, external_customer_id: str, content: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.api_url}/send_message",
            headers=self._headers(),
            json={"receiver": external_customer_id, "type": "text", "text": content},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") != 0:
            raise RuntimeError(data.get("status_message") or "Viber send failed")
        return {"external_message_id": data.get("message_token"), "raw": data}

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]:
        if payload.get("event") != "message":
            return []
        sender = payload.get("sender") or {}
        message = payload.get("message") or {}
        customer_id = str(sender.get("id", ""))
        message_id = str(payload.get("message_token", ""))
        if not customer_id or not message_id:
            return []
        return [NormalizedMessage(
            external_message_id=message_id,
            external_customer_id=customer_id,
            customer_name=sender.get("name") or "Viber user",
            content=str(message.get("text") or ""),
            message_type=str(message.get("type") or "text"),
            metadata={"provider": "viber", "raw": payload},
        )]


class YouTubeAdapter(BaseAdapter):
    channel_type = "youtube"

    def parse_webhook(self, payload: dict[str, Any]) -> list[NormalizedMessage]:
        return []

    def send_message(self, external_customer_id: str, content: str) -> dict[str, Any]:
        raise RuntimeError("YouTube does not provide a private-message channel for CRM inbox use")


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
