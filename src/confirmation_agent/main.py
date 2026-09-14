"""
Confirmation Management Agent — CLI entrypoint.

Current state: Step 1 (intake & validation), Step 2 (template selection
& drafting), and Step 3 (dispatch logging) are fully implemented and run
end-to-end against the sample workbook. Steps 4-8 are scaffolded in
their own modules with NotImplementedError bodies and detailed
docstrings — that is the next build increment, not a bug.

Step 3 defaults to a DRY RUN (no real Gmail draft or Drive upload —
placeholder ids only) so it works out of the box with no Google Cloud
setup. Pass --live once GMAIL_CREDENTIALS_PATH / AUDIT_TEAM_MAILBOX /
DRIVE_ROOT_FOLDER_ID are configured in .env (see README.md "Google
Workspace setup") to actually create drafts.

Usage:
    python -m confirmation_agent.main --input sample_data/confirmation-management-input-package.xlsx
    python -m confirmation_agent.main --input /path/to/real_engagement.xlsx --stop-after intake

    # Client workbook doesn't match io-spec.md's canonical tab/column layout:
    python -m confirmation_agent.main --input /path/to/client_export.xlsx --adapter example_client

    # Preview Step 3 dispatch (dry run, no Google credentials needed):
    python -m confirmation_agent.main --stop-after dispatch

    # Actually create Gmail drafts + Drive uploads (requires .env setup):
    python -m confirmation_agent.main --stop-after dispatch --live
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import config
from .dispatch import dispatch_all, summarize_dispatch
from .intake import load_all, summarize
from .intake_adapters import list_adapters
from .templates import draft_all, summarize_drafting

load_dotenv()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Confirmation Management Agent")
    parser.add_argument(
        "--input",
        type=Path,
        default=config.DEFAULT_SAMPLE_WORKBOOK,
        help="Path to the engagement input workbook (see docs/io-spec.md for the required tabs).",
    )
    parser.add_argument(
        "--adapter",
        default=None,
        help=(
            "Name of a registered intake adapter (src/confirmation_agent/intake_adapters/) "
            "to normalize a client workbook that doesn't match io-spec.md's canonical tab/"
            "column layout, before validation runs. Omit if the workbook already matches "
            f"io-spec.md exactly. Registered: {', '.join(list_adapters()) or '(none)'}"
        ),
    )
    parser.add_argument(
        "--stop-after",
        choices=["intake", "templates", "dispatch", "tracking", "chase", "exceptions", "reconciliation", "workpaper"],
        default="intake",
        help="Pipeline stage to stop after. Only 'intake', 'templates', and 'dispatch' are implemented today.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "Actually create Gmail drafts and Drive uploads for Step 3 (requires "
            "GMAIL_CREDENTIALS_PATH / AUDIT_TEAM_MAILBOX / DRIVE_ROOT_FOLDER_ID in .env). "
            "Without this flag, dispatch runs as a dry run with no Google API calls."
        ),
    )
    return parser


def run(input_path: Path, stop_after: str, adapter: str | None = None, live: bool = False) -> int:
    print(f"Loading and validating: {input_path}" + (f" (adapter: {adapter})" if adapter else ""))
    result = load_all(input_path, adapter=adapter)
    print(summarize(result))

    if stop_after == "intake":
        return 0

    batch = draft_all(result)
    print()
    print(summarize_drafting(batch))

    if stop_after == "templates":
        return 0

    sender = os.environ.get("AUDIT_TEAM_MAILBOX")
    drive_folder_id = os.environ.get("DRIVE_ROOT_FOLDER_ID")
    if live and not sender:
        print("\nAUDIT_TEAM_MAILBOX is not set in .env — cannot dispatch --live. See README.md 'Google Workspace setup'.")
        return 1
    if live and not drive_folder_id:
        print("\nDRIVE_ROOT_FOLDER_ID is not set in .env — cannot dispatch --live. See README.md 'Google Workspace setup'.")
        return 1

    try:
        dispatch_batch = dispatch_all(
            batch,
            result.engagement,
            drive_folder_id=drive_folder_id or "(dry-run — no Drive folder configured)",
            sender=sender or "(dry-run — no sender configured)",
            dry_run=not live,
        )
    except RuntimeError as exc:
        print(f"\nDispatch failed: {exc}")
        return 1

    print()
    print(summarize_dispatch(dispatch_batch, dry_run=not live))

    if stop_after == "dispatch":
        return 0

    print(
        f"\n--stop-after={stop_after} requested, but Steps 4-8 are not yet implemented. "
        "See docs/workflow-skill.md for the full step sequence and each module's "
        "docstring (tracking.py, chase.py, exception_schedule.py, reconciliation.py, "
        "workpaper.py) for what to build next."
    )
    return 1


def main() -> None:
    args = build_arg_parser().parse_args()
    sys.exit(run(args.input, args.stop_after, args.adapter, args.live))


if __name__ == "__main__":
    main()
