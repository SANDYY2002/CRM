from __future__ import annotations

import os
import tempfile
from pathlib import Path

from django.core.files.uploadhandler import TemporaryFileUploadHandler
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.channels.models import Channel
from apps.organizations.models import Membership

from .youtube import YouTubeAdapter


class YouTubeUploadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            organization_id = int(request.headers.get("X-Organization-ID", "0"))
        except ValueError:
            return Response({"detail": "A valid organization is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not Membership.objects.filter(organization_id=organization_id, user=request.user).exists():
            return Response({"detail": "Organization access denied."}, status=status.HTTP_403_FORBIDDEN)

        channel_id = request.data.get("channel_id")
        upload = request.FILES.get("video")
        title = request.data.get("title", "")
        description = request.data.get("description", "")
        privacy_status = request.data.get("privacy_status", "private")
        category_id = request.data.get("category_id", "22")
        tags = [tag.strip() for tag in request.data.get("tags", "").split(",") if tag.strip()]

        if not channel_id or not upload:
            return Response({"detail": "channel_id and video are required."}, status=status.HTTP_400_BAD_REQUEST)
        channel = Channel.objects.filter(id=channel_id, organization_id=organization_id, type=Channel.Types.YOUTUBE, is_active=True).first()
        if not channel:
            return Response({"detail": "Active YouTube channel not found."}, status=status.HTTP_404_NOT_FOUND)

        credentials = channel.credentials or {}
        access_token = credentials.get("access_token", "")
        refresh_token = credentials.get("refresh_token", "")
        client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        if not access_token or not refresh_token or not client_id or not client_secret:
            return Response({"detail": "YouTube OAuth is not connected for this channel."}, status=status.HTTP_409_CONFLICT)

        suffix = Path(upload.name).suffix or ".mp4"
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                for chunk in upload.chunks():
                    temp.write(chunk)
                temp_path = temp.name

            result = YouTubeAdapter(access_token, refresh_token, client_id, client_secret).upload_video(
                temp_path,
                title=title,
                description=description,
                tags=tags,
                category_id=category_id,
                privacy_status=privacy_status,
            )
            return Response(result, status=status.HTTP_201_CREATED)
        finally:
            if temp_path:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except OSError:
                    pass
