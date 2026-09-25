"""Aggregation layer: raw source frames -> report-ready tables."""
from __future__ import annotations

import pandas as pd

DELAY_MINUTES_CUTOFF = 15  # a flight is 'delayed' if it departs >15 min late


def build_daily_summary(
    flights: pd.DataFrame, passengers: pd.DataFrame
) -> pd.DataFrame:
    """One row per day: volumes, punctuality, and passenger counts."""
    f = flights.copy()
    f["delay_min"] = (f["actual_dep"] - f["scheduled_dep"]).dt.total_seconds() / 60
    f["delayed"] = f["delay_min"] > DELAY_MINUTES_CUTOFF

    daily = (
        f.groupby("flight_date")
        .agg(
            flights=("flight_id", "count"),
            delayed_flights=("delayed", "sum"),
            avg_delay_min=("delay_min", "mean"),
        )
        .reset_index()
        .rename(columns={"flight_date": "date"})
    )
    daily["delay_rate"] = daily["delayed_flights"] / daily["flights"]

    out = daily.merge(passengers, on="date", how="left")
    out["avg_delay_min"] = out["avg_delay_min"].round(1)
    out["delay_rate"] = out["delay_rate"].round(3)
    return out.sort_values("date").reset_index(drop=True)


def event_breakdown(events: pd.DataFrame) -> pd.DataFrame:
    """Ground-operations event counts per day, one column per event type."""
    return (
        events.assign(date=events["event_time"].dt.normalize())
        .groupby(["date", "event_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
