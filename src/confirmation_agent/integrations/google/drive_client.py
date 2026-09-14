"""
Google Drive API wrapper — stores drafted letters, response artifacts,
and the final workpaper.

Setup (see README.md "Google Workspace setup"):
  - Scope required: https://www.googleapis.com/auth/drive.file
    (file-scoped access — this app should only ever see files it
    creates, not the user's whole Drive)
  - Root folder id via DRIVE_ROOT_FOLDER_ID (.env), created once per
    engagement, e.g. "MSG-FY25-001 — Confirmations"
"""

from __future__ import annotations

REQUIRED_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_service():
    raise NotImplementedError("Wire up OAuth per README.md 'Google Workspace setup', mirroring gmail_client.py.")


def upload_text_file(*, filename: str, content: str, folder_id: str) -> str:
    """Upload a text/HTML letter body as a Drive file, return its file id."""
    raise NotImplementedError("service.files().create(...) with media body; return file id.")


def upload_response_artifact(*, filename: str, local_path: str, folder_id: str) -> str:
    """Upload a scanned/received response document, return its file id."""
    raise NotImplementedError("Same as upload_text_file but with a MediaFileUpload for local_path.")


def ensure_engagement_folder(engagement_code: str, root_folder_id: str) -> str:
    """Idempotently create/find the per-engagement subfolder, return its id."""
    raise NotImplementedError("List children of root_folder_id filtered by name; create if absent.")
