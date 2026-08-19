from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

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
        fields = ("id", "organization", "type", "name", "external_id", "is_active", "metadata", "created_at", "updated_at")
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
        read_only_fields = ("id", "sender", "external_id", "created_at")

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() if obj.sender else "Customer"


class OrganizationScopedViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    organization_field = "organization"

    def get_org_id(self):
        raw = self.request.query_params.get("organization") or self.request.headers.get("X-Organization-ID")
        if not raw:
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

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
    search_fields = ("first_name", "last_name", "email", "phone", "company")


class CustomerTagViewSet(OrganizationScopedViewSet):
    queryset = CustomerTag.objects.all()
    serializer_class = CustomerTagSerializer


class LeadViewSet(OrganizationScopedViewSet):
    queryset = Lead.objects.select_related("customer", "assigned_to")
    serializer_class = LeadSerializer


class ChannelViewSet(OrganizationScopedViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


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
    queryset = Message.objects.select_related("sender", "conversation")
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        org_id = self.request.query_params.get("organization") or self.request.headers.get("X-Organization-ID")
        qs = self.queryset
        if not org_id:
            return qs.none()
        return qs.filter(conversation__organization_id=org_id, conversation__organization__members=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.validated_data["conversation"]
        if not Membership.objects.filter(organization=conversation.organization, user=self.request.user).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a member of this organization.")
        message = serializer.save(sender=self.request.user, direction=Message.Direction.OUTBOUND)
        from django.utils import timezone
        Conversation.objects.filter(pk=conversation.pk).update(last_message_at=timezone.now(), updated_at=timezone.now())


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
