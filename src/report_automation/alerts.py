"""Threshold rules: the 'alert system' half of the tool.

Alerts are structured data (not just strings) so they can be rendered in
the workbook, appended to alerts.log, or pushed to email/pager from a
single source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Alert:
    date: date
    rule: str
    message: str


def evaluate_alerts(
    summary: pd.DataFrame,
    *,
    delay_rate_threshold: float,
    min_passengers_expected: int,
) -> list[Alert]:
    """Evaluate each day against the configured thresholds."""
    alerts: list[Alert] = []
    for row in summary.itertuples(index=False):
        day = row.date.date() if hasattr(row.date, "date") else row.date
        if row.delay_rate > delay_rate_threshold:
            alerts.append(Alert(
                date=day,
                rule="delay_rate",
                message=(
                    f"{day}: delay rate {row.delay_rate:.1%} exceeds "
                    f"threshold {delay_rate_threshold:.0%}"
                ),
            ))
        if row.passengers < min_passengers_expected:
            alerts.append(Alert(
                date=day,
                rule="low_volume",
                message=(
                    f"{day}: passenger volume {int(row.passengers)} below "
                    f"expected minimum {min_passengers_expected}"
                ),
            ))
    return alerts
