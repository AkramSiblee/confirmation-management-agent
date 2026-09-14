"""
Gmail API wrapper — DRAFT-ONLY by design.

This module intentionally does not implement (and should never implement)
a send function. Per docs/workflow-skill.md Section 7 (Quality standards)
and Section 11 (Cowork execution notes): "no email leaves draft status
without explicit team send action." That action happens in the user's
own Gmail client, not in this codebase.

Setup (see README.md "Google Workspace setup"):
  - OAuth client credentials JSON path via GMAIL_CREDENTIALS_PATH (.env)
  - Token cache path via GMAIL_TOKEN_PATH (.env) — shared with drive_client.py
  - Scope required: https://www.googleapis.com/auth/gmail.compose
    (compose/draft scope only — deliberately NOT gmail.send)
"""

from __future__ import annotations

import base64
from email.mime.text import MIMEText

from .auth import GMAIL_SCOPES as REQUIRED_SCOPES

__all__ = ["REQUIRED_SCOPES", "create_draft"]


def _get_service():
    """Build an authenticated Gmail API service object. Raises a clear
    RuntimeError (via auth.get_credentials) if GMAIL_CREDENTIALS_PATH is
    unset rather than falling back to any default location."""
    from googleapiclient.discovery import build

    from .auth import get_credentials

    return build("gmail", "v1", credentials=get_credentials())


def create_draft(*, to: str, subject: str, body: str, sender: str | None = None) -> str:
    """Create a Gmail draft and return its draft id.

    `sender` should be the audit-team-controlled mailbox from
    AUDIT_TEAM_MAILBOX (.env) — never a client-provided address. This
    function calls ONLY users().drafts().create — never
    users().messages().send. Do not add a send path here; see the
    module docstring and CLAUDE.md Rule 1.
    """
    if not to:
        raise ValueError("create_draft() requires a non-empty 'to' address.")

    service = _get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    if sender:
        message["from"] = sender

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft["id"]
