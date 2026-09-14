"""
Shared OAuth flow for the Gmail + Drive integration.

Both gmail_client.py and drive_client.py request the SAME combined scope
list (compose-only Gmail + file-scoped Drive) from ONE Installed-App
flow and cache a SINGLE token at GMAIL_TOKEN_PATH — whichever runs first
in a session drives the one-time browser consent, and the other reuses
the cached token, rather than needing two separate credential/token
files. See README.md "Google Workspace setup".
"""

from __future__ import annotations

import os

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
ALL_SCOPES = GMAIL_SCOPES + DRIVE_SCOPES

_ENV_CREDENTIALS_PATH = "GMAIL_CREDENTIALS_PATH"
_ENV_TOKEN_PATH = "GMAIL_TOKEN_PATH"
_DEFAULT_TOKEN_PATH = "./secrets/gmail_token.json"


def get_credentials():
    """Return valid OAuth credentials for ALL_SCOPES, refreshing or
    running the interactive consent flow as needed, and persisting the
    token back to GMAIL_TOKEN_PATH."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    credentials_path = os.environ.get(_ENV_CREDENTIALS_PATH)
    if not credentials_path:
        raise RuntimeError(
            f"{_ENV_CREDENTIALS_PATH} is not set. Copy .env.example to .env and follow "
            "README.md's 'Google Workspace setup' before dispatching for real (or pass "
            "--dry-run / omit --live to preview drafting without Google credentials)."
        )
    if not os.path.exists(credentials_path):
        raise RuntimeError(f"{_ENV_CREDENTIALS_PATH} points to '{credentials_path}', which does not exist.")

    token_path = os.environ.get(_ENV_TOKEN_PATH, _DEFAULT_TOKEN_PATH)

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ALL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, ALL_SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token_path) or ".", exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds
