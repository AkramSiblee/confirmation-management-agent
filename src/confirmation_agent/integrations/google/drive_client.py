"""
Google Drive API wrapper — stores drafted letters, response artifacts,
and the final workpaper.

Setup (see README.md "Google Workspace setup"):
  - Scope required: https://www.googleapis.com/auth/drive.file
    (file-scoped access — this app should only ever see files it
    creates, not the user's whole Drive)
  - Root folder id via DRIVE_ROOT_FOLDER_ID (.env), created once per
    engagement, e.g. "MSG-FY25-001 — Confirmations"
  - Shares OAuth credentials/token with gmail_client.py — see auth.py
"""

from __future__ import annotations

import io

from .auth import DRIVE_SCOPES as REQUIRED_SCOPES

__all__ = [
    "REQUIRED_SCOPES",
    "upload_text_file",
    "upload_response_artifact",
    "ensure_engagement_folder",
]


def _get_service():
    from googleapiclient.discovery import build

    from .auth import get_credentials

    return build("drive", "v3", credentials=get_credentials())


def upload_text_file(*, filename: str, content: str, folder_id: str) -> str:
    """Upload a text/HTML letter body as a Drive file, return its file id."""
    from googleapiclient.http import MediaIoBaseUpload

    service = _get_service()
    media = MediaIoBaseUpload(io.BytesIO(content.encode("utf-8")), mimetype="text/plain")
    file = (
        service.files()
        .create(body={"name": filename, "parents": [folder_id]}, media_body=media, fields="id")
        .execute()
    )
    return file["id"]


def upload_response_artifact(*, filename: str, local_path: str, folder_id: str) -> str:
    """Upload a scanned/received response document, return its file id."""
    from googleapiclient.http import MediaFileUpload

    service = _get_service()
    media = MediaFileUpload(local_path)
    file = (
        service.files()
        .create(body={"name": filename, "parents": [folder_id]}, media_body=media, fields="id")
        .execute()
    )
    return file["id"]


def ensure_engagement_folder(engagement_code: str, root_folder_id: str) -> str:
    """Idempotently create/find the per-engagement subfolder, return its id."""
    service = _get_service()
    query = (
        f"name = '{engagement_code}' and '{root_folder_id}' in parents "
        "and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    existing = results.get("files", [])
    if existing:
        return existing[0]["id"]

    folder = (
        service.files()
        .create(
            body={
                "name": engagement_code,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [root_folder_id],
            },
            fields="id",
        )
        .execute()
    )
    return folder["id"]
