"""
Tests for Step 3 (dispatch.py). Runs entirely in dry_run mode (no Google
OAuth/network needed) except for one test that monkeypatches
gmail_client.create_draft / drive_client.upload_text_file to prove the
"live" code path wires parameters through correctly without making a
real API call.
"""

from __future__ import annotations

from datetime import date

import pytest

from confirmation_agent import dispatch, rules
from confirmation_agent.intake import load_all
from confirmation_agent.templates import DraftedLetter, draft_all


def _letter(**overrides) -> DraftedLetter:
    defaults = dict(
        record_reference="Test Bank / ACCT-1",
        template_used="bank/us_standard.txt",
        body="letter body",
        recipient_email="bank@example.com",
        confirmation_type="bank",
        is_negative_ar=False,
    )
    defaults.update(overrides)
    return DraftedLetter(**defaults)


def test_add_business_days_skips_weekends():
    monday = date(2025, 12, 1)
    assert dispatch.add_business_days(monday, 5) == date(2025, 12, 8)


def test_resolve_first_cadence_parses_engagement_text():
    engagement = {"Chase Cadence — Bank/AR (business days)": "1st: 10 / 2nd: 20 / Escalate: 30"}
    days, assumed = dispatch._resolve_first_cadence(engagement, "Chase Cadence — Bank/AR (business days)", 999)
    assert days == 10
    assert assumed is False


def test_resolve_first_cadence_falls_back_and_flags_assumption():
    days, assumed = dispatch._resolve_first_cadence({}, "Missing Field", 15)
    assert days == 15
    assert assumed is True


def test_create_draft_and_log_dry_run_computes_due_date():
    letter = _letter()
    record = dispatch.create_draft_and_log(
        letter,
        cadence_days=10,
        drive_folder_id="folder-1",
        sender="confirmations@firm.com",
        dispatch_date=date(2025, 12, 1),
        dry_run=True,
    )
    assert record.status == "Outstanding"
    assert record.due_date == date(2025, 12, 15)  # +10 business days
    assert record.gmail_draft_id.startswith("dry-run:")
    assert record.drive_file_id.startswith("dry-run:")


def test_missing_recipient_raises_even_in_dry_run():
    letter = _letter(recipient_email="")
    with pytest.raises(dispatch.DispatchError):
        dispatch.create_draft_and_log(letter, cadence_days=10, drive_folder_id="f", sender="s", dry_run=True)


def test_negative_ar_gets_no_due_date_and_distinct_status():
    letter = _letter(confirmation_type="ar", is_negative_ar=True)
    record = dispatch.create_draft_and_log(letter, cadence_days=10, drive_folder_id="f", sender="s", dry_run=True)
    assert record.status == "Delivered — No Reply (Expected)"
    assert record.due_date is None


def test_intercompany_gets_pending_status_and_no_due_date():
    letter = _letter(confirmation_type="intercompany")
    record = dispatch.create_draft_and_log(letter, cadence_days=10, drive_folder_id="f", sender="s", dry_run=True)
    assert record.status == "Pending Component Response"
    assert record.due_date is None


def test_dispatch_all_against_sample_data_dry_run():
    result = load_all()
    batch = draft_all(result)
    dispatch_batch = dispatch.dispatch_all(
        batch,
        result.engagement,
        drive_folder_id="folder-1",
        sender="confirmations@firm.com",
        dispatch_date=date(2025, 12, 1),
        dry_run=True,
    )
    # Intercompany drafts always lack a recipient email (io-spec.md has no
    # contact column for that tab) — every one of them should land in
    # .errors, never silently dropped or given a fabricated address.
    assert len(dispatch_batch.dispatched) + len(dispatch_batch.errors) == len(batch.drafted)
    intercompany_errors = [ref for ref, _ in dispatch_batch.errors if "side)" in ref]
    assert len(intercompany_errors) == 6
    # Sample engagement's cadence fields ARE parseable — no assumption needed.
    assert dispatch_batch.assumptions == []


def test_live_path_calls_gmail_and_drive_clients(monkeypatch):
    calls = {}

    def fake_upload_text_file(*, filename, content, folder_id):
        calls["drive"] = dict(filename=filename, content=content, folder_id=folder_id)
        return "real-drive-id-123"

    def fake_create_draft(*, to, subject, body, sender=None):
        calls["gmail"] = dict(to=to, subject=subject, body=body, sender=sender)
        return "real-draft-id-456"

    monkeypatch.setattr(dispatch.drive_client, "upload_text_file", fake_upload_text_file)
    monkeypatch.setattr(dispatch.gmail_client, "create_draft", fake_create_draft)

    letter = _letter()
    record = dispatch.create_draft_and_log(
        letter,
        cadence_days=10,
        drive_folder_id="folder-1",
        sender="confirmations@firm.com",
        dry_run=False,
    )

    assert record.gmail_draft_id == "real-draft-id-456"
    assert record.drive_file_id == "real-drive-id-123"
    assert calls["gmail"]["to"] == "bank@example.com"
    assert calls["gmail"]["sender"] == "confirmations@firm.com"
    assert calls["drive"]["folder_id"] == "folder-1"
    assert calls["drive"]["content"] == "letter body"
