"""
Confirmation Management Agent — CLI entrypoint.

Current state: Step 1 (intake & validation) is fully implemented and
runs end-to-end against the sample workbook. Steps 2-8 are scaffolded
in their own modules with NotImplementedError bodies and detailed
docstrings — that is the next build increment, not a bug.

Usage:
    python -m confirmation_agent.main --input sample_data/confirmation-management-input-package.xlsx
    python -m confirmation_agent.main --input /path/to/real_engagement.xlsx --stop-after intake
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import config
from .intake import load_all, summarize


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Confirmation Management Agent")
    parser.add_argument(
        "--input",
        type=Path,
        default=config.DEFAULT_SAMPLE_WORKBOOK,
        help="Path to the engagement input workbook (see docs/io-spec.md for the required tabs).",
    )
    parser.add_argument(
        "--stop-after",
        choices=["intake", "templates", "dispatch", "tracking", "chase", "exceptions", "reconciliation", "workpaper"],
        default="intake",
        help="Pipeline stage to stop after. Only 'intake' is implemented today.",
    )
    return parser


def run(input_path: Path, stop_after: str) -> int:
    print(f"Loading and validating: {input_path}")
    result = load_all(input_path)
    print(summarize(result))

    if stop_after == "intake":
        return 0

    print(
        f"\n--stop-after={stop_after} requested, but Steps 2-8 are not yet implemented. "
        "See docs/workflow-skill.md for the full step sequence and each module's "
        "docstring (templates.py, dispatch.py, tracking.py, chase.py, exceptions.py, "
        "reconciliation.py, workpaper.py) for what to build next."
    )
    return 1


def main() -> None:
    args = build_arg_parser().parse_args()
    sys.exit(run(args.input, args.stop_after))


if __name__ == "__main__":
    main()
