"""Command-line entry point: ``ops-report`` or ``python -m report_automation``."""
from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from .exceptions import ReportAutomationError
from .pipeline import run
from .settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ops-report",
        description="Generate the weekly operations report from SQL, API, and Excel sources.",
    )
    parser.add_argument("--env-file", type=Path, default=None,
                        help="Path to a .env file (default: ./.env if present)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output workbook path (default: reports/weekly_operations_report.xlsx)")
    parser.add_argument("--alert-email", default=None,
                        help="Override the on-call alert email address")
    parser.add_argument("--offline", action="store_true",
                        help="Skip the live API and read the local snapshot")
    parser.add_argument("--log-level", default=None,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(env_file=args.env_file)

    if args.output:
        settings = replace(settings, output_file=args.output)
    if args.alert_email:
        settings = replace(settings, alert_email_to=args.alert_email)
    if args.offline:
        settings = replace(settings, api_url=None)
    if args.log_level:
        settings = replace(settings, log_level=args.log_level)

    try:
        run(settings)
    except ReportAutomationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
