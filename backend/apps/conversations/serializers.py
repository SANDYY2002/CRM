from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'external_id', 'direction',
            'message_type', 'content', 'attachment_url', 'metadata',
            'is_read', 'created_at'
        ]
        read_only_fields = ['sender', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'organization', 'customer', 'customer_name', 'channel',
            'channel_name', 'assigned_to', 'status', 'unread_count',
            'last_message_at', 'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['organization', 'unread_count', 'last_message_at', 'created_at', 'updated_at']
