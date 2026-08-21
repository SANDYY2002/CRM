from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.channels.adapters.providers import get_adapter
from apps.channels.models import Channel
from apps.conversations.models import Conversation, Message
from apps.customers.models import Customer, CustomerTag
from apps.leads.models import Lead
from apps.organizations.models import Membership, Organization

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "phone", "avatar_url", "role", "is_online")
        read_only_fields = ("id", "role", "is_online")


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "logo_url", "timezone", "created_at", "updated_at")
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    tag_ids = serializers.PrimaryKeyRelatedField(source="tags", many=True, queryset=CustomerTag.objects.all(), required=False)

    class Meta:
        model = Customer
        fields = ("id", "organization", "first_name", "last_name", "full_name", "email", "phone", "company", "avatar_url", "notes", "metadata", "tag_ids", "created_at", "updated_at")
        read_only_fields = ("id", "organization", "created_at", "updated_at")


class CustomerTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTag
        fields = ("id", "organization", "name", "color")
        read_only_fields = ("id", "organization")


class LeadSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ("id", "organization", "customer", "customer_name", "title", "status", "source", "value", "assigned_to", "assigned_to_name", "description", "created_at", "updated_at")
        read_only_fields = ("id", "organization", "created_at", "updated_at")

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("id", "organization", "type", "name", "external_id", "is_active", "credentials", "metadata", "created_at", "updated_at")
        read_only_fields = ("id", "organization", "created_at", "updated_at")
        extra_kwargs = {"credentials": {"write_only": True}}


class ConversationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    channel_name = serializers.CharField(source="channel.name", read_only=True)
    channel_type = serializers.CharField(source="channel.type", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "organization", "customer", "customer_name", "channel", "channel_name", "channel_type", "assigned_to", "assigned_to_name", "status", "unread_count", "last_message_at", "created_at", "updated_at")
        read_only_fields = ("id", "organization", "last_message_at", "created_at", "updated_at")

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ("id", "conversation", "sender", "sender_name", "external_id", "direction", "message_type", "content", "attachment_url", "metadata", "is_read", "created_at")
        read_only_fields = ("id", "sender", "external_id", "created_at", "direction")

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else "Customer"


def resolve_organization_id(request):
    """Resolve the active workspace safely.

    An explicit organization header/query value always wins. If the authenticated
    user belongs to exactly one organization, that organization can be inferred
    when an older/local browser session has not persisted the workspace ID yet.
    Multi-organization users must explicitly select a workspace.
    """
    raw = request.query_params.get("organization") or request.headers.get("X-Organization-ID")
    if raw:
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    organization_ids = list(
        Membership.objects.filter(user=request.user).values_list("organization_id", flat=True)[:2]
    )
    if len(organization_ids) == 1:
        return organization_ids[0]
    return None


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    organization_field = "organization"

    def get_org_id(self):
        return resolve_organization_id(self.request)

    def get_queryset(self):
        queryset = super().get_queryset()
        org_id = self.get_org_id()
        if org_id is None:
            return queryset.none()
        if not Membership.objects.filter(organization_id=org_id, user=self.request.user).exists():
            return queryset.none()
        return queryset.filter(**{self.organization_field: org_id})

    def perform_create(self, serializer):
        org_id = self.get_org_id()
        if org_id is None or not Membership.objects.filter(organization_id=org_id, user=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"organization": "A valid organization membership is required."})
        serializer.save(organization_id=org_id)


class CustomerViewSet(OrganizationScopedViewSet):
    queryset = Customer.objects.select_related("organization").prefetch_related("tags")
    serializer_class = CustomerSerializer


class CustomerTagViewSet(OrganizationScopedViewSet):
    queryset = CustomerTag.objects.all()
    serializer_class = CustomerTagSerializer


class LeadViewSet(OrganizationScopedViewSet):
    queryset = Lead.objects.select_related("customer", "assigned_to")
    serializer_class = LeadSerializer


class ChannelViewSet(OrganizationScopedViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    @action(detail=True, methods=["post"])
    def health(self, request, pk=None):
        channel = self.get_object()
        credentials = channel.credentials or {}
        required = {
            Channel.Types.FACEBOOK: ("access_token", "app_secret", "send_endpoint"),
            Channel.Types.INSTAGRAM: ("access_token", "app_secret", "send_endpoint"),
            Channel.Types.WHATSAPP: ("access_token", "phone_number_id"),
            Channel.Types.VIBER: ("auth_token",),
            Channel.Types.YOUTUBE: ("access_token", "refresh_token"),
        }.get(channel.type, ())
        missing = [key for key in required if not credentials.get(key)]
        return Response({
            "id": channel.id,
            "type": channel.type,
            "connected": channel.is_active and not missing,
            "missing": missing,
            "external_id": channel.external_id,
        })


class ConversationViewSet(OrganizationScopedViewSet):
    queryset = Conversation.objects.select_related("customer", "channel", "assigned_to")
    serializer_class = ConversationSerializer

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        conversation.unread_count = 0
        conversation.messages.filter(is_read=False, direction=Message.Direction.INBOUND).update(is_read=True)
        conversation.save(update_fields=["unread_count", "updated_at"])
        return Response(ConversationSerializer(conversation).data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related("sender", "conversation__channel", "conversation__customer")
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        org_id = resolve_organization_id(self.request)
        if org_id is None:
            return self.queryset.none()
        return self.queryset.filter(conversation__organization_id=org_id, conversation__organization__members=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        conversation = serializer.validated_data["conversation"]
        if not Membership.objects.filter(organization=conversation.organization, user=self.request.user).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a member of this organization.")

        content = serializer.validated_data.get("content", "").strip()
        if not content:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"content": "Message content is required."})

        external_ids = (conversation.customer.metadata or {}).get("external_ids") or {}
        external_customer_id = external_ids.get(conversation.channel.type)
        if not external_customer_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"conversation": "The customer is not connected to this channel yet."})

        adapter = get_adapter(conversation.channel.type, conversation.channel.credentials or {})
        try:
            provider_result = adapter.send_message(str(external_customer_id), content)
        except Exception as exc:
            from rest_framework.exceptions import APIException
            raise APIException({"detail": f"Provider delivery failed: {exc}"}) from exc

        message = serializer.save(
            sender=self.request.user,
            direction=Message.Direction.OUTBOUND,
            external_id=str(provider_result.get("external_message_id") or ""),
            metadata={"provider_delivery": provider_result.get("raw", provider_result)},
        )
        Conversation.objects.filter(pk=conversation.pk).update(last_message_at=timezone.now(), updated_at=timezone.now())

        payload = MessageSerializer(message).data
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(f"conversation_{conversation.pk}", {"type": "message_event", "message": payload})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    org_id = resolve_organization_id(request)
    if org_id is None:
        return Response({"detail": "A valid organization is required."}, status=status.HTTP_400_BAD_REQUEST)
    if not Membership.objects.filter(organization_id=org_id, user=request.user).exists():
        return Response({"detail": "Organization access denied."}, status=status.HTTP_403_FORBIDDEN)
    conversations = Conversation.objects.filter(organization_id=org_id)
    leads = Lead.objects.filter(organization_id=org_id)
    customers = Customer.objects.filter(organization_id=org_id)
    unread = Message.objects.filter(conversation__organization_id=org_id, is_read=False, direction=Message.Direction.INBOUND).count()
    recent_messages = Message.objects.filter(conversation__organization_id=org_id).select_related("conversation__customer", "conversation__channel").order_by("-created_at")[:8]
    return Response({
        "organization_id": org_id,
        "stats": {"conversations": conversations.count(), "customers": customers.count(), "leads": leads.count(), "unread_messages": unread},
        "recent_activity": [{"id": m.id, "customer": m.conversation.customer.full_name, "channel": m.conversation.channel.type, "content": m.content, "direction": m.direction, "created_at": m.created_at} for m in recent_messages],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"user": UserSerializer(request.user).data, "organizations": OrganizationSerializer(request.user.organizations.all(), many=True).data})


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email", "")
    organization_name = request.data.get("organization_name")
    first_name = request.data.get("first_name", "")
    last_name = request.data.get("last_name", "")
    if not username or not password or not organization_name:
        return Response({"detail": "username, password and organization_name are required."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, role=User.Roles.OWNER)
        base_slug = slugify(organization_name) or "workspace"
        slug = base_slug
        counter = 2
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        organization = Organization.objects.create(name=organization_name, slug=slug)
        Membership.objects.create(organization=organization, user=user, role="owner")
    refresh = RefreshToken.for_user(user)
    return Response({"user": UserSerializer(user).data, "organization": OrganizationSerializer(organization).data, "access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({"user": UserSerializer(user).data, "organizations": OrganizationSerializer(user.organizations.all(), many=True).data, "access": str(refresh.access_token), "refresh": str(refresh)})
