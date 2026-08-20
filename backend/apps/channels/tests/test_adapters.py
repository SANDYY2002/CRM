import hashlib
import hmac
import json

from django.test import SimpleTestCase

from apps.channels.adapters.providers import FacebookAdapter, InstagramAdapter, ViberAdapter, WhatsAppAdapter


class ProviderAdapterTests(SimpleTestCase):
    def test_facebook_inbound_message_is_normalized(self):
        adapter = FacebookAdapter({})
        payload = {"entry": [{"messaging": [{"sender": {"id": "cust-1"}, "message": {"mid": "m-1", "text": "Hello"}}]}]}
        messages = adapter.parse_webhook(payload)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].external_customer_id, "cust-1")
        self.assertEqual(messages[0].external_message_id, "m-1")
        self.assertEqual(messages[0].content, "Hello")

    def test_instagram_ignores_echo(self):
        adapter = InstagramAdapter({})
        payload = {"entry": [{"messaging": [{"sender": {"id": "cust-1"}, "message": {"mid": "m-1", "text": "sent", "is_echo": True}}]}]}
        self.assertEqual(adapter.parse_webhook(payload), [])

    def test_whatsapp_inbound_message_is_normalized(self):
        adapter = WhatsAppAdapter({})
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"wa_id": "9779800000000", "profile": {"name": "Test User"}}],
                        "messages": [{"from": "9779800000000", "id": "wamid-1", "type": "text", "text": {"body": "Hello CRM"}}],
                    }
                }]
            }]
        }
        messages = adapter.parse_webhook(payload)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].customer_name, "Test User")
        self.assertEqual(messages[0].content, "Hello CRM")

    def test_viber_signature_is_validated(self):
        token = "test-token"
        body = json.dumps({"event": "message"}).encode()
        signature = hmac.new(token.encode(), body, hashlib.sha256).hexdigest()
        adapter = ViberAdapter({"auth_token": token})
        self.assertTrue(adapter.verify_webhook({"X-Viber-Content-Signature": signature}, body))
        self.assertFalse(adapter.verify_webhook({"X-Viber-Content-Signature": "bad"}, body))
