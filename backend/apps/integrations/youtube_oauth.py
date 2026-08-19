from __future__ import annotations

import os

from django.core import signing
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.channels.models import Channel
from apps.organizations.models import Membership, Organization

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
STATE_SALT = "crm-youtube-oauth"
STATE_MAX_AGE = 600


def _client_config() -> dict:
    return {
        "web": {
            "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [os.getenv("YOUTUBE_REDIRECT_URI", "")],
        }
    }


class YouTubeOAuthUrlView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            organization_id = int(request.headers.get("X-Organization-ID", "0"))
        except ValueError:
            return Response({"detail": "A valid organization is required."}, status=400)
        if not Membership.objects.filter(organization_id=organization_id, user=request.user).exists():
            return Response({"detail": "Organization access denied."}, status=403)

        if not os.getenv("YOUTUBE_CLIENT_ID") or not os.getenv("YOUTUBE_CLIENT_SECRET") or not os.getenv("YOUTUBE_REDIRECT_URI"):
            return Response({"detail": "YouTube OAuth environment variables are not configured."}, status=503)

        flow = Flow.from_client_config(_client_config(), scopes=[YOUTUBE_SCOPE], redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI"))
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=signing.dumps({"user_id": request.user.id, "organization_id": organization_id}, salt=STATE_SALT),
        )
        return Response({"authorization_url": authorization_url})


class YouTubeOAuthCallbackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        frontend = os.getenv("FRONTEND_URL", "http://localhost:5173")
        error = request.query_params.get("error")
        if error:
            return redirect(f"{frontend}/settings?youtube=error&reason={error}")

        try:
            payload = signing.loads(request.query_params.get("state", ""), salt=STATE_SALT, max_age=STATE_MAX_AGE)
        except signing.BadSignature:
            return redirect(f"{frontend}/settings?youtube=error&reason=invalid_state")

        flow = Flow.from_client_config(_client_config(), scopes=[YOUTUBE_SCOPE], redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI"))
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
        channel_response = youtube.channels().list(part="snippet", mine=True).execute()
        channel_items = channel_response.get("items", [])
        if not channel_items:
            return redirect(f"{frontend}/settings?youtube=error&reason=no_channel")

        remote = channel_items[0]
        snippet = remote.get("snippet") or {}
        organization = Organization.objects.get(pk=payload["organization_id"])
        Channel.objects.update_or_create(
            organization=organization,
            type=Channel.Types.YOUTUBE,
            external_id=remote.get("id", ""),
            defaults={
                "name": snippet.get("title") or "YouTube Channel",
                "is_active": True,
                "credentials": {
                    "access_token": credentials.token or "",
                    "refresh_token": credentials.refresh_token or "",
                },
                "metadata": {
                    "channel_id": remote.get("id"),
                    "thumbnail": (snippet.get("thumbnails") or {}).get("default", {}).get("url", ""),
                },
            },
        )
        return redirect(f"{frontend}/settings?youtube=connected")
