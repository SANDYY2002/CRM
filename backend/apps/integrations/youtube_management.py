from __future__ import annotations

import os
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from apps.channels.models import Channel
from apps.organizations.models import Membership


def youtube_service(channel: Channel):
    credentials = channel.credentials or {}
    if not credentials.get("access_token") or not credentials.get("refresh_token"):
        raise ValueError("YouTube channel is not authenticated.")
    client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise ValueError("YouTube OAuth server credentials are not configured.")
    creds = Credentials(
        token=credentials.get("access_token"),
        refresh_token=credentials.get("refresh_token"),
        token_uri=credentials.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=client_id,
        client_secret=client_secret,
        scopes=credentials.get("scope", "").split() or None,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        channel.credentials = {
            **credentials,
            "access_token": creds.token,
            "token_uri": creds.token_uri,
        }
        channel.save(update_fields=["credentials", "updated_at"])
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def get_channel(request, channel_id: int) -> Channel | None:
    try:
        organization_id = int(request.headers.get("X-Organization-ID", "0"))
    except ValueError:
        return None
    if not Membership.objects.filter(organization_id=organization_id, user=request.user).exists():
        return None
    return Channel.objects.filter(id=channel_id, organization_id=organization_id, type=Channel.Types.YOUTUBE, is_active=True).first()


class YouTubeVideosView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, channel_id: int):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        try:
            youtube = youtube_service(channel)
            search = youtube.search().list(part="snippet", forMine=True, type="video", maxResults=min(int(request.query_params.get("limit", "25")), 50)).execute()
            ids = [item.get("id", {}).get("videoId") for item in search.get("items", []) if item.get("id", {}).get("videoId")]
            details = youtube.videos().list(part="snippet,status,contentDetails,statistics", id=",".join(ids)).execute() if ids else {"items": []}
            return Response({"items": details.get("items", []), "nextPageToken": search.get("nextPageToken")})
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)


class YouTubeVideoDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, channel_id: int, video_id: str):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        try:
            response = youtube_service(channel).videos().list(part="snippet,status,contentDetails,statistics", id=video_id).execute()
            items = response.get("items", [])
            if not items:
                return Response({"detail": "Video not found."}, status=404)
            return Response(items[0])
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)

    def patch(self, request, channel_id: int, video_id: str):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        payload = request.data
        snippet = payload.get("snippet") or {}
        status_body = payload.get("status") or {}
        body = {"id": video_id, "snippet": snippet, "status": status_body}
        try:
            result = youtube_service(channel).videos().update(part="snippet,status", body=body).execute()
            return Response(result)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)

    def delete(self, request, channel_id: int, video_id: str):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        try:
            youtube_service(channel).videos().delete(id=video_id).execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)


class YouTubeCommentsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, channel_id: int, video_id: str):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        try:
            response = youtube_service(channel).commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(int(request.query_params.get("limit", "50")), 100),
                textFormat="plainText",
            ).execute()
            return Response(response)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)

    def post(self, request, channel_id: int, video_id: str):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        text = str(request.data.get("text", "")).strip()
        if not text:
            return Response({"detail": "text is required."}, status=400)
        try:
            response = youtube_service(channel).commentThreads().insert(
                part="snippet",
                body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": text}}}},
            ).execute()
            return Response(response, status=201)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)


class YouTubeReplyView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, channel_id: int, comment_id: str):
        channel = get_channel(request, channel_id)
        if not channel:
            return Response({"detail": "YouTube channel not found or access denied."}, status=404)
        text = str(request.data.get("text", "")).strip()
        if not text:
            return Response({"detail": "text is required."}, status=400)
        try:
            response = youtube_service(channel).comments().insert(
                part="snippet",
                body={"snippet": {"parentId": comment_id, "textOriginal": text}},
            ).execute()
            return Response(response, status=201)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=502)
