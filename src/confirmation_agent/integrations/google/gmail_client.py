"""
Gmail API wrapper — DRAFT-ONLY by design.

This module intentionally does not implement (and should never implement)
a send function. Per docs/workflow-skill.md Section 7 (Quality standards)
and Section 11 (Cowork execution notes): "no email leaves draft status
without explicit team send action." That action happens in the user's
own Gmail client, not in this codebase.

Setup (see README.md "Google Workspace setup"):
  - OAuth client credentials JSON path via GMAIL_CREDENTIALS_PATH (.env)
  - Token cache path via GMAIL_TOKEN_PATH (.env)
  - Scope required: https://www.googleapis.com/auth/gmail.compose
    (compose/draft scope only — deliberately NOT gmail.send)
"""

from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText

REQUIRED_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def _get_service():
    """Build an authenticated Gmail API service object.

    NOT YET IMPLEMENTED. Use google-auth-oauthlib's InstalledAppFlow
    with REQUIRED_SCOPES, caching the token at GMAIL_TOKEN_PATH. Raise
    a clear error if GMAIL_CREDENTIALS_PATH is unset rather than
    falling back to any default location.
    """
    raise NotImplementedError("Wire up OAuth per README.md 'Google Workspace setup'.")


def create_draft(*, to: str, subject: str, body: str, sender: str | None = None) -> str:
    """Create a Gmail draft and return its draft id.

    `sender` should be the audit-team-controlled mailbox from
    AUDIT_TEAM_MAILBOX (.env) — never a client-provided address. This
    function must never call users.messages.send — only
    users.drafts.create.
    """
    raise NotImplementedError(
        "service = _get_service(); build a MIMEText message, base64-encode it, "
        "and call service.users().drafts().create(userId='me', body={...}).execute(). "
        "Return the resulting draft id for the DispatchRecord."
    )
