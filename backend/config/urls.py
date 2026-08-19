from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import (
    ChannelViewSet,
    ConversationViewSet,
    CustomerTagViewSet,
    CustomerViewSet,
    LeadViewSet,
    MessageViewSet,
    dashboard,
    login,
    me,
    register,
)
from apps.channels.webhooks import channel_webhook
from apps.integrations.youtube_api import YouTubeUploadView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok', 'service': 'crm-api'})


router = routers.DefaultRouter()
router.register('customers', CustomerViewSet, basename='customer')
router.register('customer-tags', CustomerTagViewSet, basename='customer-tag')
router.register('leads', LeadViewSet, basename='lead')
router.register('channels', ChannelViewSet, basename='channel')
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthView.as_view(), name='health'),
    path('api/auth/register/', register, name='register'),
    path('api/auth/login/', login, name='login'),
    path('api/auth/me/', me, name='me'),
    path('api/dashboard/', dashboard, name='dashboard'),
    path('api/webhooks/channel/<int:channel_id>/', channel_webhook, name='channel-webhook'),
    path('api/youtube/upload/', YouTubeUploadView.as_view(), name='youtube-upload'),
    path('api/', include(router.urls)),
]
