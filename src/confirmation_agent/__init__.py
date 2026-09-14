"""Confirmation Management Agent -- bank/AR/legal external confirmations
and intercompany balance agreement for multi-jurisdiction group audits.

See docs/workflow-skill.md for methodology and docs/io-spec.md for the
input/output specification. CLAUDE.md documents the non-negotiable
design rules a Claude Code session should not relax while building out
the remaining steps.
"""

from .intake import IntakeResult, ValidationIssue, load_all, summarize

__version__ = "0.1.0"

__all__ = ["IntakeResult", "ValidationIssue", "load_all", "summarize", "__version__"]
