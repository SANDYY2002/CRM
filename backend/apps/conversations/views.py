from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


def current_org(request):
    return request.user.organizations.first()


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = current_org(self.request)
        if not org:
            return Conversation.objects.none()
        return Conversation.objects.filter(organization=org).select_related('customer', 'channel', 'assigned_to').prefetch_related('messages')

    def perform_create(self, serializer):
        org = current_org(self.request)
        if not org:
            raise ValueError('User is not a member of an organization.')
        serializer.save(organization=org)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        conversation.unread_count = 0
        conversation.save(update_fields=['unread_count', 'updated_at'])
        conversation.messages.filter(is_read=False, direction=Message.Direction.INBOUND).update(is_read=True)
        return Response(ConversationSerializer(conversation).data)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = current_org(self.request)
        if not org:
            return Message.objects.none()
        return Message.objects.filter(conversation__organization=org).select_related('conversation', 'sender')

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        conversation = get_object_or_404(self.get_queryset().model._meta.get_field('conversation').remote_field.model, pk=conversation_id)
        if conversation.organization != current_org(self.request):
            return Response({'detail': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)
        message = serializer.save(sender=self.request.user, direction=Message.Direction.OUTBOUND)
        Conversation.objects.filter(pk=conversation.pk).update(last_message_at=timezone.now(), updated_at=timezone.now())
        return message
