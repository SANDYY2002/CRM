from __future__ import annotations

from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"


class YouTubeAdapter:
    """Real YouTube Data API v3 upload/manage adapter.

    The CRM stores OAuth token material on the connected Channel. Client ID and
    client secret stay in backend environment variables.
    """

    def __init__(self, access_token: str, refresh_token: str, client_id: str, client_secret: str):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[YOUTUBE_UPLOAD_SCOPE],
        )
        self.client_id = client_id
        self.client_secret = client_secret

    def service(self):
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
        return build("youtube", "v3", credentials=self.credentials, cache_discovery=False)

    def upload_video(
        self,
        file_path: str | Path,
        *,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        category_id: str = "22",
        privacy_status: str = "private",
    ) -> dict[str, Any]:
        if privacy_status not in {"private", "public", "unlisted"}:
            raise ValueError("privacy_status must be private, public, or unlisted")
        if not title.strip():
            raise ValueError("title is required")

        youtube = self.service()
        body = {
            "snippet": {
                "title": title.strip(),
                "description": description,
                "tags": tags or [],
                "categoryId": category_id,
            },
            "status": {"privacyStatus": privacy_status},
        }
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(str(file_path), resumable=True),
        )
        response = None
        while response is None:
            _, response = request.next_chunk()

        return {
            "id": response.get("id"),
            "title": (response.get("snippet") or {}).get("title"),
            "privacy_status": (response.get("status") or {}).get("privacyStatus"),
            "raw": response,
        }
