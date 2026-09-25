"""Orchestration: sources -> aggregates -> alerts -> rendered report."""
from __future__ import annotations

import logging
import time
from pathlib import Path

from .alerts import evaluate_alerts
from .logging_config import setup_logging
from .notify import notify_alerts, notify_failure
from .reporting import build_daily_summary, event_breakdown
from .settings import Settings
from .sources import load_all
from .writer import write_report


def run(settings: Settings) -> Path:
    """Execute one full report cycle; returns the output workbook path."""
    logger = setup_logging(settings.logs_dir, settings.log_level)
    started = time.perf_counter()
    logger.info("Run started")

    try:
        sources = load_all(settings, logger)
        summary = build_daily_summary(sources["flights"], sources["passengers"])
        events = event_breakdown(sources["events"])

        alerts = evaluate_alerts(
            summary,
            delay_rate_threshold=settings.delay_rate_threshold,
            min_passengers_expected=settings.min_passengers_expected,
        )
        notify_alerts(logger, alerts, settings)

        output = write_report(
            summary, events, alerts, settings.output_file,  # type: ignore[arg-type]
            delay_rate_threshold=settings.delay_rate_threshold,
        )
        logger.info("Report written to %s", output)
    except Exception as exc:
        notify_failure(logger, settings, exc)
        raise

    elapsed = time.perf_counter() - started
    logger.info("Run finished in %.2fs", elapsed)
    print(f"Report generated: {output} ({elapsed:.2f}s)")
    print("Manual equivalent: ~2 hours of copy-paste per weekly cycle.")
    return output
